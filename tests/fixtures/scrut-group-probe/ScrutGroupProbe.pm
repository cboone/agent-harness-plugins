package ScrutGroupProbe;

use strict;
use warnings;
use POSIX ();
use Errno qw(EPERM EACCES);

# Inject failures at the runner's real child-side setpgid call. The race mode
# fails a redundant call after Bash job control has already made this a leader.
my $setpgid = \&POSIX::setpgid;
{
    no warnings 'redefine';
    *POSIX::setpgid = sub {
        my $mode = $ENV{SCRUT_GROUP_PROBE_MODE} // die "missing probe mode\n";
        open my $log, '>>', $ENV{SCRUT_GROUP_PROBE_LOG} or die "probe log: $!\n";
        print {$log} "setpgid\n";
        close $log or die "probe log: $!\n";
        if ($mode eq 'eperm' || ($mode eq 'race' && getpgrp(0) == $$)) {
            $! = EPERM;
            return undef;
        }
        if ($mode eq 'eacces') {
            $! = EACCES;
            return undef;
        }
        if ($mode eq 'wait') {
            open my $pid, '>', $ENV{SCRUT_GROUP_PROBE_PID} or die "probe pid: $!\n";
            print {$pid} "$$\n";
            close $pid or die "probe pid: $!\n";
            sleep 30;
        }
        my $result = $setpgid->(@_);
        die "probe: group not established\n" if defined($result) && getpgrp(0) != $$;
        $ARGV[0] = '/nonexistent/run-scrut-wrapper' if $mode eq 'exec';
        return $result;
    };
}

1;
