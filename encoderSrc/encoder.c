/*  Get the first bit of every item and arrange them in a new array. */
void encode(unsigned char *in_array, unsigned char *out_array, int size){
    const unsigned char mask = 0x80;
    const unsigned char shift = 7;
    unsigned int tempByte;
    unsigned int i;

    for(i=0;i<size;i++){

        tempByte <<= 1;
        tempByte |= in_array[i] & mask;

        if((i+1) %8 == 0){
            tempByte >>= shift;
            tempByte &= 0xFF;
            out_array[i/8] = tempByte;
            tempByte = 0;
        }
    }
}
