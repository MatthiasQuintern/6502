opcodes_d = {

        # branches
        0xf0:   "beq r",
        0xd0:   "bne r",
        # jump
        0x4c:   "jmp a",
        0x20:   "jsr s",
        0x60:   "rts s",
        # load
        0xad:   "lda a",
        0xa9:   "lda #",
        0xa2:   "ldx #",
        # store
        0x8d:   "sta a",
        # compare
        0xc9:   "cmp #",
        # increments
        0xee:   "inc a",
        0x1a:   "inc A",
        0xe8:   "inx i",

}
