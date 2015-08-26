#!/usr/bin/perl
use IO::Socket::INET;
use Time::HiRes qw(time);

my $mySocket=new IO::Socket::INET->new(LocalPort=>1234,
        Proto=>'udp');

my $threshold=5;
my $interval=1;
my $debug = 1;
my $print_jitter_interval = 5;

my $expcount=1; my $exptime=time();
my $lastime=time(); $lastpacket = 0;
while ( 1) {
        $mySocket->recv($text,1500);
        my $bytes= length($text);
        my ($instr,$var1, $var2, $var3, $var4) = split(/:/,$text);
        if ($instr eq 'DATA') {
                my ($count,$time,$payload, $cks) = ($var1, $var2, $var3, $var4);
                if ($cks ne chksum($payload)) {
                        print sprintf "checksum error [$cks] %s $count $time $payload\n" , chksum($payload);
                }
                if ($expcount != $count) {
                        my $dropped = $count-$expcount;
                        my $int = $dropped * $interval;
                        my $now = time();
                        if ($dropped > $threshold) {
                                print "$now Gap: $dropped packets, $int ms ($time, $count, $expcount)\n";
                                my $localtgap = ($now - $lasttime)*1000;
                                my $localpgap = $count - $lastpacket;
                                printf "Gap seen locally is $localtgap ($now - $lasttime), $localpgap ($count - $lastpacket)\n";
                        }
                } else {
                        $lasttime=time(); $lastpacket=$count;
                        my $gap = $time - $exptime;
                        if ($count % (1000*$print_jitter_interval/$interval) == 1 ){
                                print "jitter gap $gap ($count $time)\n";
                        }
                }
                $expcount = $count+1;
                $exptime = time()+$interval/1000;
        } elsif ($instr eq 'RSTTMR') {
                print "Setting Timer Interval to $interval\n" if $debug;
                $interval=$var1;
        } else {
                print "Unknown Instruction $instr\n";
        }
#       print "received packet $count\n";
}

exit;

sub chksum {
  my ($string) = @_;
  my $v = 0;
  $v ^= $_ for unpack 'C*', $string;
  my $ret = sprintf '%02X', $v;
  return $ret;
}

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
