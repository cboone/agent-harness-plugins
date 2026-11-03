package ScrutGroupProbe;

use strict;
use warnings;
use POSIX ();
use Errno qw(EPERM EACCES ENOSPC EPIPE);

# Inject failures at the runner's real child-side setpgid call. The race mode
# fails a redundant call after Bash job control has already made this a leader.
# Inject publication/readiness failures in the anchor, before the wrapper execs.
{
    no warnings 'redefine';
    *CORE::GLOBAL::fork = sub () {
        my $child = CORE::fork();
        my $mode = $ENV{SCRUT_GROUP_PROBE_MODE} // '';
        if (defined($child) && $mode =~ /^anchor-/) {
            if (!$child) {
                $SIG{PIPE} = 'DEFAULT' if $mode eq 'anchor-brokenpipe';
                open my $pid, '>', $ENV{SCRUT_GROUP_PROBE_PID} or die "probe pid: $!\n";
                print {$pid} "$$\n";
                close $pid or die "probe pid close: $!\n";
                if ($mode eq 'anchor-stopped') {
                    my $stopped = 0;
                    for (1..100) {
                        open my $state, '-|', 'ps', '-p', getppid(), '-o', 'stat='
                            or die "probe ps: $!\n";
                        my $value = <$state> // '';
                        close $state;
                        if ($value =~ /T/) { $stopped = 1; last; }
                        select undef, undef, undef, 0.01;
                    }
                    die "probe wrapper did not stop\n" unless $stopped;
                }
            } elsif ($mode eq 'anchor-stopped') {
                kill 'STOP', $$;
            }
        }
        return $child;
    };
    *CORE::GLOBAL::syswrite = sub (*$;$$) {
        my ($handle, $buffer, $length, $offset) = @_;
        my $mode = $ENV{SCRUT_GROUP_PROBE_MODE} // '';
        if ($mode eq 'anchor-publish' && $buffer =~ /^[1-9][0-9]*\n$/) {
            $! = ENOSPC;
            return undef;
        }
        if ($buffer eq '1') {
            if ($mode eq 'anchor-ready') { $! = ENOSPC; return undef; }
            if ($mode eq 'anchor-timeout') { sleep 30; }
            if ($mode eq 'anchor-brokenpipe') {
                my $resumed = 0;
                for (1..200) {
                    if (-e "$ENV{SCRUT_GROUP_PROBE_LOG}.resume") { $resumed = 1; last; }
                    select undef, undef, undef, 0.05;
                }
                die "probe readiness write was not resumed\n" unless $resumed;
                open my $log, '>>', $ENV{SCRUT_GROUP_PROBE_LOG} or die "probe log: $!\n";
                print {$log} "ready write attempted\n";
                close $log or die "probe log close: $!\n";
                my $written = CORE::syswrite($handle, $buffer);
                my $error = 0 + $!;
                open $log, '>>', $ENV{SCRUT_GROUP_PROBE_LOG} or die "probe log: $!\n";
                print {$log} "ready write returned EPIPE\n" if !defined($written) && $error == EPIPE;
                close $log or die "probe log close: $!\n";
                $! = $error;
                return $written;
            }
        }
        return CORE::syswrite($handle, $buffer, $length, $offset) if @_ == 4;
        return CORE::syswrite($handle, $buffer, $length) if @_ == 3;
        return CORE::syswrite($handle, $buffer);
    };
}

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
