void encodeRGB3d_C(unsigned char *in_array, unsigned char *out_array,
                   int height, int size, int bits, int bitsDone){
    /* Get the first n bits of a RGB bytes sequence,
    return another sequence ordered by bit number
    (6 MSB bytes, 6 next-bit bytes).
    The information for each uC is crossed, one byte for each and repeat.
    */
    if(bitsDone>=bits || !bits || bits > 8)
        return;

    unsigned char *out_array_shifted = out_array+bitsDone*6;

    unsigned char shift = 8-bits;
    unsigned char mask = 1 << shift;
    unsigned int tempByteEven = 0;
    unsigned int tempByteOdd = 0;
    unsigned int i;

    for(i=0;i<size;){

        tempByteEven <<= 1;
        tempByteEven |= in_array[i] & mask;
        i++;

        tempByteOdd <<= 1;
        tempByteOdd |= in_array[i] & mask;
        i++;

        if(i %16 == 0){
            tempByteEven >>= shift;
            tempByteEven &= 0xFF;

            tempByteOdd >>= shift;
            tempByteOdd &= 0xFF;

            out_array_shifted[(i/16-1)*bits] = tempByteEven;
            out_array_shifted[(i/16+7)*bits] = tempByteOdd;

            tempByteOdd = 0;
            tempByteEven = 0;
        }
    }

    /* Yay, recursion! */
    if(bits>1){
        encodeRGB3d_C(in_array,out_array,height,size,bits,bitsDone+1);
    }
}

void encodeRGB3dI_C(unsigned char *in_array, unsigned char *out_array,
                    int height, int size, int bits, int bitsDone){
    /* Get the first n bits of a RGB bytes sequence,
    return another sequence ordered by bit number (MSB first),
    and with the even-column bits first, then the odd's (Interlaced).
    */
    if(bitsDone>=bits || !bits || bits > 8)
        return;

    unsigned char *out_array_shifted = out_array+bitsDone*6;

    unsigned char shift = 8-bits;
    unsigned char mask = 1 << shift;
    unsigned int tempByteEven = 0;
    unsigned int tempByteOdd = 0;
    unsigned int i;

    /* Interlaced transmission variables */
    const unsigned int columnBytes = height * 3 * bits / 8;
    const unsigned int columnBits = columnBytes * 8;
    unsigned int offset = 0;
    unsigned char isOdd = 1;
    unsigned int indexEven;
    unsigned int indexOdd;

    for(i=0;i<size;){

        if(i % columnBits == 0){
            isOdd = !isOdd;
            if (!isOdd && i)
                offset += columnBytes;
        }

        tempByteEven <<= 1;
        tempByteEven |= in_array[i] & mask;
        i++;

        tempByteOdd <<= 1;
        tempByteOdd |= in_array[i] & mask;
        i++;

        if(i %16 == 0){
            tempByteEven >>= shift;
            tempByteEven &= 0xFF;

            tempByteOdd >>= shift;
            tempByteOdd &= 0xFF;

            indexEven = offset+((i/16-1)*bits)%columnBytes;
            indexOdd = offset+((i/16+7)*bits)%columnBytes;

            out_array_shifted[indexEven] = tempByteEven;
            out_array_shifted[indexOdd] = tempByteOdd;

            tempByteOdd = 0;
            tempByteEven = 0;
        }
    }

    /* Yay, recursion! */
    if(bits>1){
        encodeRGB3dI_C(in_array,out_array,height,size,bits,bitsDone+1);
    }
}
