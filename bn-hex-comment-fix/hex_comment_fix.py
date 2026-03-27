"""
hex_comment_fix.py  –  Binary Ninja Plugin
=============================================

Fixes the rendering overlap bug where 0x hex numbers in comments cause
subsequent text to visually overlap.

ROOT CAUSE ANALYSIS:
  Binary Ninja's C++ core may tokenize 0x hex patterns inside comments as
  PossibleAddressToken / IntegerToken, which are rendered differently from
  plain CommentToken. Additionally, InstructionTextToken.width defaults to
  len(text), which miscounts CJK double-width characters (each CJK char
  occupies 2 monospace cells but len() counts it as 1).

TWO-PRONGED FIX:

  1. ZWSP Insertion (primary) – via BinaryDataNotification:
     Inserts an invisible zero-width space (U+200B) between '0' and 'x' in
     comment text.  This breaks BN's hex pattern recogniser so the text is
     rendered as plain CommentToken instead of PossibleAddressToken.
     Invisible to the user; does not add visible spaces.

  2. Render Layer (secondary) – display-time safety net:
     • Converts any IntegerToken / PossibleAddressToken that appear inside
       comment sections back to CommentToken.
     • Corrects the `width` field on every CommentToken to account for CJK
       double-width characters (using unicodedata.east_asian_width).

USAGE:
  After restarting Binary Ninja:
  • Render layer is always active (View → Render Layers → "Hex Comment Fix")
  • Run "Plugins → Hex Comment Fix → Enable Auto-Fix" once per binary to:
    - Batch-fix all existing comments (ZWSP insertion)
    - Register auto-fixer for new/edited comments
  • Run "Plugins → Hex Comment Fix → Undo All Fixes" to remove all ZWSP
  • Run "Plugins → Hex Comment Fix → Debug: Dump Tokens" to inspect tokens
"""

import re
import unicodedata
from typing import List

from binaryninja import (
    BinaryDataNotification,
    BinaryView,
    Function,
    RenderLayer,
    RenderLayerDefaultEnableState,
    InstructionTextToken,
    InstructionTextTokenType,
    DisassemblyTextLine,
    PluginCommand,
    log_info,
    log_error,
)


# ═══════════════════════════════════════════════════════════════════════════════
#  Constants
# ═══════════════════════════════════════════════════════════════════════════════

ZWSP = '\u200B'                              # Zero-Width Space
_HEX_RE = re.compile(r'0([xX][0-9a-fA-F])')  # 0x/0X followed by hex digit

_NUMERIC_TYPES = frozenset({
    InstructionTextTokenType.IntegerToken,
    InstructionTextTokenType.PossibleAddressToken,
    InstructionTextTokenType.FloatingPointToken,
})


# ═══════════════════════════════════════════════════════════════════════════════
#  Part 1 — ZWSP Comment Modification (Primary Fix)
# ═══════════════════════════════════════════════════════════════════════════════

_active_notifiers = []          # prevent GC from destroying notifiers


def _fix_text(text: str) -> str:
    """Insert ZWSP between 0 and x: '0x50' → '0\\u200Bx50'.  Idempotent."""
    if not text or ZWSP in text:
        return text
    return _HEX_RE.sub(lambda m: '0' + ZWSP + m.group(1), text)


def _unfix_text(text: str) -> str:
    """Remove all ZWSP from text (undo)."""
    return text.replace(ZWSP, '') if text else text


class _HexCommentNotifier(BinaryDataNotification):
    """Auto-fix comments as they are created/edited."""

    def __init__(self):
        super().__init__()
        self._busy = False

    def data_metadata_updated(self, view, offset):
        if self._busy:
            return
        comment = view.get_comment_at(offset)
        if not comment:
            return
        fixed = _fix_text(comment)
        if fixed != comment:
            self._busy = True
            try:
                view.set_comment_at(offset, fixed)
            finally:
                self._busy = False

    def function_updated(self, view, func):
        if self._busy:
            return
        try:
            comments = func.comments
        except Exception:
            return
        if not comments:
            return
        self._busy = True
        try:
            for addr, text in dict(comments).items():
                fixed = _fix_text(text)
                if fixed != text:
                    func.set_comment_at(addr, fixed)
        finally:
            self._busy = False


def _cmd_enable_autofix(bv):
    """Batch-fix all existing comments + register auto-fixer."""
    count = 0

    # Address comments
    for addr, text in dict(bv.address_comments).items():
        fixed = _fix_text(text)
        if fixed != text:
            bv.set_comment_at(addr, fixed)
            count += 1

    # Function comments
    for func in bv.functions:
        for addr, text in dict(func.comments).items():
            fixed = _fix_text(text)
            if fixed != text:
                func.set_comment_at(addr, fixed)
                count += 1

    # Register notifier for future comments
    notifier = _HexCommentNotifier()
    bv.register_notification(notifier)
    _active_notifiers.append(notifier)

    log_info(f'[HexFix] Batch-fixed {count} comments.  Auto-fix enabled.')


def _cmd_undo_all(bv):
    """Remove all ZWSP from comments."""
    count = 0

    for addr, text in dict(bv.address_comments).items():
        if ZWSP in text:
            bv.set_comment_at(addr, _unfix_text(text))
            count += 1

    for func in bv.functions:
        for addr, text in dict(func.comments).items():
            if ZWSP in text:
                func.set_comment_at(addr, _unfix_text(text))
                count += 1

    log_info(f'[HexFix] Removed ZWSP from {count} comments.')


# ═══════════════════════════════════════════════════════════════════════════════
#  Part 2 — Render Layer (Secondary / Safety-Net Fix)
# ═══════════════════════════════════════════════════════════════════════════════

def _display_width(text: str) -> int:
    """Monospace display width: East-Asian Wide/Fullwidth = 2 cells, else 1."""
    w = 0
    for ch in text:
        eaw = unicodedata.east_asian_width(ch)
        w += 2 if eaw in ('W', 'F') else 1
    return w


def _clone_token(tok, **kw):
    """Clone an InstructionTextToken, overriding specified fields."""
    return InstructionTextToken(
        kw.get('type', tok.type),
        kw.get('text', tok.text),
        kw.get('value', tok.value),
        kw.get('size', tok.size),
        kw.get('operand', tok.operand),
        kw.get('context', tok.context),
        kw.get('address', tok.address),
        kw.get('confidence', tok.confidence),
        list(getattr(tok, 'typeNames', [])),
        kw.get('width', tok.width),
        getattr(tok, 'il_expr_index', 0xffffffffffffffff),
    )


def _fix_tokens(tokens):
    """
    Walk a token list.  Once inside a comment section:
      - Fix width of every CommentToken for CJK double-width chars
      - Convert IntegerToken / PossibleAddressToken to CommentToken
    """
    in_comment = False
    out = []
    changed = False

    for tok in tokens:
        # Detect comment section start (the ';' separator)
        if tok.type == InstructionTextTokenType.CommentToken:
            in_comment = True
            correct_w = _display_width(tok.text)
            if correct_w != tok.width:
                out.append(_clone_token(tok, width=correct_w))
                changed = True
                continue

        if in_comment and tok.type in _NUMERIC_TYPES:
            # PossibleAddressToken may display resolved symbol name → restore hex
            if tok.type == InstructionTextTokenType.PossibleAddressToken:
                try:
                    txt = hex(tok.value)
                except Exception:
                    txt = tok.text
            else:
                txt = tok.text
            out.append(_clone_token(tok,
                type=InstructionTextTokenType.CommentToken,
                text=txt,
                width=_display_width(txt),
            ))
            changed = True
            continue

        out.append(tok)

    return out if changed else tokens


class HexCommentFixRenderLayer(RenderLayer):
    """Render layer that fixes 0x overlap and CJK width in comments."""

    name = "Hex Comment Fix"
    default_enable_state = (
        RenderLayerDefaultEnableState.EnabledByDefaultRenderLayerDefaultEnableState
    )

    def apply_to_block(self, block, lines):
        """Handles disasm / LLIL / MLIL / HLIL blocks (graph + linear)."""
        for line in lines:
            try:
                line.tokens = _fix_tokens(line.tokens)
            except Exception as e:
                log_error(f'[HexFix] block: {e}')
        return lines

    def apply_to_high_level_il_body(self, function, lines):
        """HLIL linear view — tokens live in line.contents.tokens."""
        for line in lines:
            try:
                line.contents.tokens = _fix_tokens(line.contents.tokens)
            except Exception as e:
                log_error(f'[HexFix] hlil_body: {e}')
        return lines


# ═══════════════════════════════════════════════════════════════════════════════
#  Part 3 — Debug Helper
# ═══════════════════════════════════════════════════════════════════════════════

def _cmd_debug_tokens(bv):
    """Dump token info for every line that contains a comment (first function)."""
    for func in bv.functions:
        log_info(f'[HexFix DBG] === Function: {func.name} @ {hex(func.start)} ===')
        for line in func.get_disassembly_text():
            has_comment = any(
                t.type == InstructionTextTokenType.CommentToken for t in line.tokens
            )
            if has_comment:
                log_info(f'[HexFix DBG] --- line @ {hex(line.address)} ---')
                for i, t in enumerate(line.tokens):
                    log_info(
                        f'  [{i:2d}] type={t.type!r:48s} '
                        f'text={t.text!r:30s} width={t.width:3d} value={t.value:#x}'
                    )
        break  # first function only


# ═══════════════════════════════════════════════════════════════════════════════
#  Registration
# ═══════════════════════════════════════════════════════════════════════════════

HexCommentFixRenderLayer.register()

PluginCommand.register(
    "Hex Comment Fix\\Enable Auto-Fix",
    "Fix all 0x hex overlap in existing+future comments (inserts invisible ZWSP)",
    _cmd_enable_autofix,
)

PluginCommand.register(
    "Hex Comment Fix\\Undo All Fixes",
    "Remove all ZWSP insertions from comments",
    _cmd_undo_all,
)

PluginCommand.register(
    "Hex Comment Fix\\Debug: Dump Comment Tokens",
    "Print token details for comment lines to the BN log (first function)",
    _cmd_debug_tokens,
)

log_info(
    '[HexFix] Plugin loaded — render layer active.  '
    'Run "Plugins > Hex Comment Fix > Enable Auto-Fix" per binary for full fix.'
)
