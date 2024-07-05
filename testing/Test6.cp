def int gcd(int a, int b)
int r;
if (a<0) then a = 3*a fi;
if (b<0) then b = 2*b fi;

if (a<b) then r=a; a=b; b=r fi;
while (b<>0) do
	r = a % b;
	=b;
	b=r;
od;
return(a)
fed;

int x,y,z;
x=12; y=15;

z=gcd(x+y,y);
print(z);
y=2*3+x;
z=gcd(x+y, y);
print(z);


z=gcd(x+y, x);
print(z)
.