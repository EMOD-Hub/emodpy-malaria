
#  'A', 'C', 'G', 'T'
barcodes = [
    "TAAAAAAAAATAAAAAAAAAAAAAATAAAAAAAAAAAAAAAAAAAAAAATAAAAAAAAAAAAAAAAAAAAAATAA",
    "TAAAAAATAAAAAAAAAAAAAAAAATAAAAAAAAAAAAAAAAAAAAAAATAAAAAAAAAAAAAAATAAAAAAAAA",
    "TAAAAATAAAAAAAAAAAAAAAAAATAAAAAAAAAAAAAAAAAAAAAAATAAAAAAAAAAAAAAAAAATAAAAAA"
]
barcode_index = 0


def get_next_barcode():
    global barcode_index
    barcode_index += 1
    return barcodes[barcode_index % len(barcodes)]