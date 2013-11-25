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
    unsigned int tempByteOdd = 0;
    unsigned int tempByteEven = 0;
    unsigned int countO = 0;
    unsigned int countE = 0;
    unsigned int i;

    // Odd
    for(i=0;i<(size/2);i++){

        tempByte <<= 1;
        tempByte |= in_array[(i/3)*6+2-i%3] & mask;

        if((i+1) %8 == 0){
            tempByte >>= shift;
            tempByte &= 0xFF;
            out_array_section[i/4-1] = tempByte;
            tempByte = 0;
        }
    }

    // Even
    for(i=0;i<(size/2);i++){

        tempByte <<= 1;
        tempByte |= in_array[(i/3)*6+5-i%3] & mask;

        if((i+1) %8 == 0){
            tempByte >>= shift;
            tempByte &= 0xFF;
            out_array_section[i/4] = tempByte;
            tempByte = 0;
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
    *
    /**/
}
