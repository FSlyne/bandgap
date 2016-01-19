#!/usr/bin/perl
use IO::Socket::INET;
use Time::HiRes qw(time alarm sleep);

my $dest='10.0.0.123';
my $alt='10.10.10.10';
my $port=9090;
my $max=1000000;
#
my $payload=randPayload(1500);

my $debug=1;
my $packetsize=30;
my $delay=0.001; my $delayms = $delay*1000;
my $sendevery=1/$delay;

my $mySocket=new IO::Socket::INET->new(PeerPort=>$port,
        Proto=>'udp',
        PeerAddr=>$dest);

my $altSocket=new IO::Socket::INET->new(PeerPort=>$port,
        Proto=>'udp',
        PeerAddr=>$alt);

my $totalbytes=0; my $t= time();
#
setInterval($delayms);
#
$SIG{ALRM} = sub {
        alarm $delay;
        my $msg="DATA:".$count++.":".time().":";
        setInterval($delayms) if $count % $sendevery == 1;
#       $msg .= substr($payload,0,$packetsize-length($msg));
        $msg=createMsg($msg);
        $mySocket->send($msg);
        $totalbytes+=$packetsize;
};

alarm $delay;

sleep 1 while 1;


exit;

sub chksum {
  my ($string) = @_;
  my $v = 0;
  $v ^= $_ for unpack 'C*', $string;
  my $ret = sprintf '%02X', $v;
  return $ret;
}

sub createMsg {
my $msg = shift;
my $p = substr($payload,0,$packetsize-length($msg));
my $cks = chksum($p);
return $msg.$p.':'.$cks;
}

sub setInterval {
my $int = shift;
my $msg = "RSTTMR:".$int.":".time().":";;
$msg=createMsg($msg);
$mySocket->send($msg);
$totalbytes+=$packetsize;
}

sub randPayload {
my $size = shift;

my @chars = ("A".."Z", "a".."z");
my $string;
$string .= $chars[rand @chars] for 1..$size;
return $string;
}
