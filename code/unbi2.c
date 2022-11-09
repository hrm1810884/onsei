#include <stdio.h>
#include <stdlib.h>
#include <math.h>
int main(int argc,char **argv){
    // if(argc != 2){
    //     errno = EINVAL;
    //     perror("Needs two command line argument");
    //     exit(EXIT_FAILURE);
    // }
    // int N = 10000;
    // short data[N];
    // int n;
    // int fd = open(argv[1],O_RDONLY);
    // while(true){
    //     n = read(fd,data,N);
    //     if(n==-1){
    //         perror("read");exit(1);
    //     }
    //     else if(n == 0){
    //         break;
    //     }else{
    //         for(int i = 0;i < 512;i++){
    //             printf("%d\n",(int)(data[i]));
    //         }
    //         break;
    //     }
    // }
    // close(fd);
    // return 0;
      /* check the format of input */
  if (argc != 4)
    {
      fprintf(stderr, "Usage: %s DATfile skip[sample] frame_length[sample]\n", argv[0]);
      exit(1);
    }
  FILE* fpDAT;
  int nskip;
  int framelen;
  int i;
  
  /* check the validity of input */
  if( ( fpDAT = fopen( argv[1], "r" ) ) == NULL )  exit( 1 );
  if( ( nskip    = atoi( argv[2] ) ) < 0 )  exit( 1 );
  if( ( framelen = atoi( argv[3] ) ) < 0 )  exit( 1 );

  fprintf( stderr, "# DATfile = %s\n", argv[1] );
  fprintf( stderr, "# %d samples are skipped.\n", nskip );
  fprintf( stderr, "# 1 frame contains %d sampels.\n", framelen );

  /* memory allocation & initilization */
  /* calloc() puts zero-values for assigned memories. */
  short *data = (short*)calloc( framelen, sizeof(short) );
  if ( data == NULL ) exit (1);

  fseek( fpDAT, nskip*sizeof(short), SEEK_SET );
  fread( data, sizeof(short), framelen, fpDAT);
  fclose( fpDAT );
  for(i=0;i<framelen;i++){
      printf("%d %d\n",i,(int)data[i]);
  }

}
