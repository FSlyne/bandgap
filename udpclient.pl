#!/usr/bin/perl
use IO::Socket::INET;
use Time::HiRes qw(time);

my $mySocket=new IO::Socket::INET->new(LocalPort=>1234,
        Proto=>'udp');

my $interval=1;

my $expcount=1; my $exptime=time();
while ( 1) {
        $mySocket->recv($text,1500);
        my $bytes= length($text);
        my ($instr,$var1, $var2, $var3) = split(/:/,$text);
        if ($instr eq 'DATA') {
                my ($count,$time,$payload) = ($var1, $var2, $var3);
                if ($expcount != $count) {
                        my $dropped = $count-$expcount;
                        my $int = $dropped * $interval;
                        print "Gap: $dropped packets, $int ms ($time, $count, $expcount)\n";
                } else {
                        my $gap = $time - $exptime;
                        print "jitter gap $gap\n" if $count % 100 ==1;
                }
                $expcount = $count+1;
                $exptime = time()+$interval/1000;
        } elsif ($instr eq 'RSTTMR') {
                print "Setting Timer Interval to $interval\n";
                $interval=$var1;
        }
#       print "received packet $count\n";
}

exit;

sub convms {
my $sec=shift;
return sprintf("%.3f",$sec*1000);
}

sub convspeed {
my $bytes=shift;
my $bits=$bytes*8;
my $units = "bps";
if ($bits < 1e3) {
        $units = "bps";
} elsif ($bits < 1e6) {
        $bits = $bits/1e3;
        $units = "kbps";
} elsif ($bits < 1e9) {
        $bits = $bits/1e6;
        $units = "Mbps";
} elsif ($bits < 1e12) {
        $bits = $bits/1e9;
        $units = "Gbps";
}
$bits=sprintf("%.1f",$bits);
return "$bits $units";
}
