void encodeRGB3d_C(unsigned char *in_array, unsigned char *out_array, int bits, int size){
    /* Get the first n bits of a RGB bytes sequence,
    return another sequence ordered by bit number (LSB first),
    and with the even-column bits first, then the odd's.
    */
    if(!bits || bits > 8)
        return;

    unsigned char shift = 8-bits;
    unsigned char mask = 1 << shift;
    unsigned int tempByte = 0;
    unsigned int i;

    /* Interlaced transmission variables */
    unsigned int oddOffset = size / 2;
    unsigned char isOdd;

    for(i=0;i<size;i++){
        // Send the
        //offset = i < size/2 ? i * 2 : i / 2

        tempByte <<= 1;
        tempByte |= in_array[i] & mask;

        if((i+1) %8 == 0){
            tempByte >>= shift;
            tempByte &= 0xFF;
            out_array[i/8] = tempByte;
            tempByte = 0;
        }
    }

    /* Yeah, recursion! */
    if(bits>1){
        encodeRGB3d_C(in_array,out_array+size/8,bits-1,size);
    }
}
