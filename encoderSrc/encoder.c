void encodeRGB3d_C(unsigned char *in_array, unsigned char *out_array, int bits, int height, int size){
    /* Get the first n bits of a RGB bytes sequence,
    return another sequence ordered by bit number (MSB first).
    */
    if(!bits || bits > 8)
        return;

    unsigned char *out_array_section = out_array+(bits-1)*size/8;

    unsigned char shift = 8-bits;
    unsigned char mask = 1 << shift;
    unsigned int tempByte = 0;
    unsigned int i;

    for(i=0;i<size;i++){

        tempByte <<= 1;
        tempByte |= in_array[i] & mask;

        if((i+1) %8 == 0){
            tempByte >>= shift;
            tempByte &= 0xFF;
            out_array_section[i/8] = tempByte;
            tempByte = 0;
        }
    }

    /* Yay, recursion! */
    if(bits>1){
        encodeRGB3d_C(in_array,out_array,bits-1,height,size);
    }
}

void encodeRGB3dI_C(unsigned char *in_array, unsigned char *out_array, int bits, int height, int size){
    /* Get the first n bits of a RGB bytes sequence,
    return another sequence ordered by bit number (MSB first),
    and with the even-column bits first, then the odd's (Interlaced).
    */
    if(!bits || bits > 8)
        return;

    unsigned char *out_array_section = out_array+(bits-1)*size/8;

    unsigned char shift = 8-bits;
    unsigned char mask = 1 << shift;
    unsigned int tempByte = 0;
    unsigned int i;

    /* Interlaced transmission variables */
    const unsigned int columnBytes = height * 3 / 8;
    const unsigned int columnBits = columnBytes * 8;
    unsigned int offset = 0;
    unsigned char isOdd = 1;
    unsigned int index;

    for(i=0;i<size;i++){

        if(i % columnBits == 0){
            isOdd = !isOdd;
            if (!isOdd && i)
                offset += columnBytes;
        }

        tempByte <<= 1;
        tempByte |= in_array[i] & mask;

        if((i+1) %8 == 0){
            tempByte >>= shift;
            tempByte &= 0xff;
            index = offset+(i/8)%columnBytes;
            out_array_section[index] = tempByte;
            tempByte = 0;
        }
    }

    /* Yay, recursion! */
    if(bits>1){
        encodeRGB3dI_C(in_array,out_array,bits-1,height,size);
    }
}
