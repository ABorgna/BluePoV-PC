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

<<<<<<< HEAD
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
=======
    // This is slowly becoming a spaghetti
    for(i=0;i<size;){   /* rgb */
        tempByteOdd <<= 1;
        tempByteOdd |= in_array[i+2] & mask;    /* b */
        if(!(++countO %8)){
            tempByteOdd >>= shift;
            tempByteOdd &= 0xFF;
            out_array_shifted[((countO/8-1)*2)*bits] = tempByteOdd;
            tempByteOdd = 0;
        }
        i++;

        tempByteOdd <<= 1;
        tempByteOdd |= in_array[i] & mask;      /* g */
        if(!(++countO %8)){
            tempByteOdd >>= shift;
            tempByteOdd &= 0xFF;
            out_array_shifted[((countO/8-1)*2)*bits] = tempByteOdd;
            tempByteOdd = 0;
        }
        i++;

        tempByteOdd <<= 1;
        tempByteOdd |= in_array[i-2] & mask;    /* r */
        if(!(++countO %8)){
            tempByteOdd >>= shift;
            tempByteOdd &= 0xFF;
            out_array_shifted[((countO/8-1)*2)*bits] = tempByteOdd;
            tempByteOdd = 0;
        }
        i++;

        tempByteEven <<= 1;
        tempByteEven |= in_array[i+2] & mask;   /* b */
        if(!(++countE %8)){
            tempByteEven >>= shift;
            tempByteEven &= 0xFF;
            out_array_shifted[((countE/8-1)*2+1)*bits] = tempByteEven;
            tempByteEven = 0;
        }
        i++;

        tempByteEven <<= 1;
        tempByteEven |= in_array[i] & mask;     /* g */
        if(!(++countE %8)){
            tempByteEven >>= shift;
            tempByteEven &= 0xFF;
            out_array_shifted[((countE/8-1)*2+1)*bits] = tempByteEven;
            tempByteEven = 0;
        }
        i++;

        tempByteEven <<= 1;
        tempByteEven |= in_array[i-2] & mask;   /* r */
        if(!(++countE %8)){
            tempByteEven >>= shift;
            tempByteEven &= 0xFF;
            out_array_shifted[((countE/8-1)*2+1)*bits] = tempByteEven;
            tempByteEven = 0;
>>>>>>> 3686ceae591e20929b9406b796a0a79d30838ad7
        }
        i++;
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
<<<<<<< HEAD
    if(!bits || bits > 8)
=======
    if(bitsDone>=bits || !bits || bits > 8)
>>>>>>> 3686ceae591e20929b9406b796a0a79d30838ad7
        return;

    unsigned char *out_array_shifted = out_array+bitsDone*6;

    unsigned char shift = 8-bits;
    unsigned char mask = 1 << shift;
    unsigned int tempByteEven = 0;
    unsigned int tempByteOdd = 0;
    unsigned int i;

    /* Interlaced transmission variables *
<<<<<<< HEAD
    const unsigned int columnBytes = height * 3 / 8;
=======
    const unsigned int columnBytes = height * 3 * bits / 8;
>>>>>>> 3686ceae591e20929b9406b796a0a79d30838ad7
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

    /* Yay, recursion! *
    if(bits>1){
        encodeRGB3dI_C(in_array,out_array,height,size,bits,bitsDone+1);
    }
    /**/
<<<<<<< HEAD
=======
    ;
>>>>>>> 3686ceae591e20929b9406b796a0a79d30838ad7
}
