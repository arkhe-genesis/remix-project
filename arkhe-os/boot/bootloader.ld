/* Linker script for ARKHE OS bootloader */
ENTRY(_start)

SECTIONS {
    . = 0x7C00; /* Typical MBR load address */

    .text : {
        *(.text)
    }

    .rodata : {
        *(.rodata)
    }

    .data : {
        *(.data)
    }

    .bss : {
        *(.bss)
    }

    /* Boot signature */
    .sig : AT(0x7DFE) {
        SHORT(0xAA55);
    }
}
