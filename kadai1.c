#include <stdio.h>
#include <stdlib.h>
#include <math.h>

double autocor(short *sdata, int tau, int framelen);

double autocor(short *sdata, int tau, int framelen)
{
  double ans = 0.0;
  for (int i = 0; i < framelen - tau; i++)
  {
    ans += sdata[i] * sdata[i + tau];
  }
  return ans;
}

int main(int argc, char **argv)
{
  /* check the format of input */
  if (argc != 4)
  {
    fprintf(stderr, "Usage: %s DATfile skip[sample] frame_length[sample]\n", argv[0]);
    exit(1);
  }
  FILE *fpDAT;
  int nskip;
  int framelen;
  int i;

  /* check the validity of input */
  if ((fpDAT = fopen(argv[1], "r")) == NULL)
    exit(1);
  if ((nskip = atoi(argv[2])) < 0)
    exit(1);
  if ((framelen = atoi(argv[3])) < 0)
    exit(1);

  fprintf(stderr, "# DATfile = %s\n", argv[1]);
  fprintf(stderr, "# %d samples are skipped.\n", nskip);
  fprintf(stderr, "# 1 frame contains %d sampels.\n", framelen);

  /* memory allocation & initilization */
  /* calloc() puts zero-values for assigned memories. */
  short *sdata = (short *)calloc(framelen, sizeof(short));
  if (sdata == NULL)
    exit(1);

  fseek(fpDAT, nskip * sizeof(short), SEEK_SET);
  fread(sdata, sizeof(short), framelen, fpDAT);

    // for ( i = 0 ; i < framelen; i++)
    //   {
    //     sdata[i] = (0.54-0.46*cos(2*M_PI*i/(framelen-1))) *sdata[i];
    //   }
    // double r_0 = autocor(sdata,0,framelen);
    // for(int t=0;t<framelen;t++){
    //     printf("%f %lf\n", (double)t/16000, autocor(sdata,t,framelen)/r_0);
    // }
  for (int skip = 0; skip < 20; skip++)
  {
    nskip += framelen/2;
    fseek(fpDAT, nskip * sizeof(short), SEEK_SET);
    fread(sdata, sizeof(short), framelen, fpDAT);
    for (i = 0; i < framelen; i++)
    {
      sdata[i] = (0.54 - 0.46 * cos(2 * M_PI * i / (framelen - 1))) * sdata[i];
    }
    double r_0 = autocor(sdata, 0, framelen);
    int t,pre_t;
    pre_t = 0;
    double pre_tmp, tmp;
    double T;
    pre_tmp = 1; //=r_0/r_0（初期値）
    int flag = 0;
    double sum = 0.0;
    int count = 0;
    for (t = 1; t < framelen; t++){
      tmp = autocor(sdata, t, framelen) / r_0;
      if (pre_tmp <= tmp){
        flag = 1;
      }else if(pre_tmp > tmp && flag == 1){
        // printf("%d %d\n",skip,t);
        sum += (t-pre_t);
        count += 1;
        pre_t = t;
        flag = 0;
      }else{
        flag = 0;
      }
      pre_tmp = tmp;
    }
    T = sum/count;
    printf("%d %f\n", skip,log10(16000/T));
  }
  fclose(fpDAT);
}