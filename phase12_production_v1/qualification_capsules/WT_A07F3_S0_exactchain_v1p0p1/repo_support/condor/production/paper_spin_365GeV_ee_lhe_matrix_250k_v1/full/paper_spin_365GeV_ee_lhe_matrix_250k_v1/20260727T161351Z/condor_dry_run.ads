
ClusterId=1
In="/dev/null"
Cmd="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/scripts/production/run_production_shard.sh"
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0000.1.0.err"
Iwd="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0000.1.0.out"
Args="--sample-id ee_ttbar_epmum_LR100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 0 --seed 365251000 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
Rank=0.0
Owner=undefined
QDate=1785168858
MyType="Job"
JobPrio=0
UserLog="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/whizard_production.condor.log"
MaxHosts=1
MinHosts=1
NumCkpts=0
DiskUsage=16
ImageSize=13
StreamErr=false
StreamOut=false
ExitStatus=0
JobFlavour="tomorrow"
OnExitHold=(ExitBySignal == true) || (ExitCode != 0)
TargetType="Machine"
TransferIn=false
Environment="PYTHONDONTWRITEBYTECODE=1;KEY4HEP_SETUP=/cvmfs/sw.hsf.org/key4hep/setup.sh"
JobUniverse=5
NumRestarts=0
RequestCpus=1
RequestDisk=DiskUsage
CurrentHosts=0
ExitBySignal=false
JobBatchName="whizard_365ee_250k_v1"
NumJobStarts=0
RemoteSysCpu=0.0
Requirements=(TARGET.Arch == "X86_64") && (TARGET.OpSys == "LINUX") && (TARGET.Disk >= RequestDisk) && (TARGET.Memory >= RequestMemory) && (TARGET.HasFileTransfer)
CommittedTime=0
CondorVersion="$CondorVersion: 24.12.16 2026-01-29 BuildID: 869053 PackageID: 24.12.16-1 GitSHA: d5741e8b $"
JobSubmitFile="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/whizard_production.sub"
RemoteUserCpu=0.0
RequestMemory=3000
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in"
CondorPlatform="$CondorPlatform: x86_64_AlmaLinux9 $"
ExecutableSize=13
NumSystemHolds=0
SendCredential=true
TransferOutput=""
JobNotification=0
JobSubmitMethod=0
LeaveJobInQueue=false
PeriodicRelease=false
JobLeaseDuration=2400
TotalSuspensions=0
CommittedSlotTime=0
NumJobCompletions=0
CumulativeSlotTime=0
LastSuspensionTime=0
RemoteWallClockTime=0.0
ShouldTransferFiles="YES"
TransferInputSizeMB=0
EnteredCurrentStatus=1785168858
WhenToTransferOutput="ON_EXIT"
CumulativeRemoteSysCpu=0.0
CommittedSuspensionTime=0
CumulativeRemoteUserCpu=0.0
CumulativeSuspensionTime=0
ProcId=0
JobStatus=1

ProcId=1
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0001.1.1.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0001.1.1.out"
Args="--sample-id ee_ttbar_epmum_LR100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 1 --seed 365251001 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"

ProcId=2
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0002.1.2.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0002.1.2.out"
Args="--sample-id ee_ttbar_epmum_LR100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 2 --seed 365251002 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"

ProcId=3
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0003.1.3.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0003.1.3.out"
Args="--sample-id ee_ttbar_epmum_LR100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 3 --seed 365251003 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"

ProcId=4
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0004.1.4.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0004.1.4.out"
Args="--sample-id ee_ttbar_epmum_LR100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 4 --seed 365251004 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"

ProcId=5
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0005.1.5.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0005.1.5.out"
Args="--sample-id ee_ttbar_epmum_LR100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 5 --seed 365251005 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"

ProcId=6
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0006.1.6.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0006.1.6.out"
Args="--sample-id ee_ttbar_epmum_LR100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 6 --seed 365251006 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"

ProcId=7
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0007.1.7.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0007.1.7.out"
Args="--sample-id ee_ttbar_epmum_LR100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 7 --seed 365251007 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"

ProcId=8
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0008.1.8.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0008.1.8.out"
Args="--sample-id ee_ttbar_epmum_LR100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 8 --seed 365251008 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"

ProcId=9
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0009.1.9.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0009.1.9.out"
Args="--sample-id ee_ttbar_epmum_LR100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 9 --seed 365251009 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"

ProcId=10
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0010.1.10.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0010.1.10.out"
Args="--sample-id ee_ttbar_epmum_LR100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 10 --seed 365251010 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"

ProcId=11
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0011.1.11.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0011.1.11.out"
Args="--sample-id ee_ttbar_epmum_LR100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 11 --seed 365251011 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"

ProcId=12
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0012.1.12.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0012.1.12.out"
Args="--sample-id ee_ttbar_epmum_LR100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 12 --seed 365251012 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"

ProcId=13
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0013.1.13.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0013.1.13.out"
Args="--sample-id ee_ttbar_epmum_LR100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 13 --seed 365251013 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"

ProcId=14
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0014.1.14.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0014.1.14.out"
Args="--sample-id ee_ttbar_epmum_LR100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 14 --seed 365251014 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"

ProcId=15
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0015.1.15.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0015.1.15.out"
Args="--sample-id ee_ttbar_epmum_LR100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 15 --seed 365251015 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"

ProcId=16
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0016.1.16.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0016.1.16.out"
Args="--sample-id ee_ttbar_epmum_LR100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 16 --seed 365251016 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"

ProcId=17
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0017.1.17.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0017.1.17.out"
Args="--sample-id ee_ttbar_epmum_LR100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 17 --seed 365251017 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"

ProcId=18
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0018.1.18.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0018.1.18.out"
Args="--sample-id ee_ttbar_epmum_LR100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 18 --seed 365251018 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"

ProcId=19
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0019.1.19.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0019.1.19.out"
Args="--sample-id ee_ttbar_epmum_LR100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 19 --seed 365251019 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"

ProcId=20
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0020.1.20.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0020.1.20.out"
Args="--sample-id ee_ttbar_epmum_LR100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 20 --seed 365251020 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"

ProcId=21
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0021.1.21.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0021.1.21.out"
Args="--sample-id ee_ttbar_epmum_LR100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 21 --seed 365251021 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"

ProcId=22
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0022.1.22.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0022.1.22.out"
Args="--sample-id ee_ttbar_epmum_LR100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 22 --seed 365251022 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"

ProcId=23
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0023.1.23.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0023.1.23.out"
Args="--sample-id ee_ttbar_epmum_LR100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 23 --seed 365251023 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"

ProcId=24
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0024.1.24.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_sc_ISR_365GeV/shard_0024.1.24.out"
Args="--sample-id ee_ttbar_epmum_LR100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 24 --seed 365251024 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"

ProcId=25
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0000.1.25.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0000.1.25.out"
Args="--sample-id ee_ttbar_epmum_LR100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 0 --seed 365252000 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in"

ProcId=26
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0001.1.26.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0001.1.26.out"
Args="--sample-id ee_ttbar_epmum_LR100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 1 --seed 365252001 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in"

ProcId=27
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0002.1.27.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0002.1.27.out"
Args="--sample-id ee_ttbar_epmum_LR100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 2 --seed 365252002 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in"

ProcId=28
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0003.1.28.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0003.1.28.out"
Args="--sample-id ee_ttbar_epmum_LR100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 3 --seed 365252003 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in"

ProcId=29
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0004.1.29.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0004.1.29.out"
Args="--sample-id ee_ttbar_epmum_LR100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 4 --seed 365252004 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in"

ProcId=30
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0005.1.30.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0005.1.30.out"
Args="--sample-id ee_ttbar_epmum_LR100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 5 --seed 365252005 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in"

ProcId=31
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0006.1.31.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0006.1.31.out"
Args="--sample-id ee_ttbar_epmum_LR100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 6 --seed 365252006 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in"

ProcId=32
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0007.1.32.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0007.1.32.out"
Args="--sample-id ee_ttbar_epmum_LR100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 7 --seed 365252007 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in"

ProcId=33
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0008.1.33.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0008.1.33.out"
Args="--sample-id ee_ttbar_epmum_LR100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 8 --seed 365252008 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in"

ProcId=34
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0009.1.34.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0009.1.34.out"
Args="--sample-id ee_ttbar_epmum_LR100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 9 --seed 365252009 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in"

ProcId=35
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0010.1.35.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0010.1.35.out"
Args="--sample-id ee_ttbar_epmum_LR100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 10 --seed 365252010 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in"

ProcId=36
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0011.1.36.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0011.1.36.out"
Args="--sample-id ee_ttbar_epmum_LR100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 11 --seed 365252011 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in"

ProcId=37
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0012.1.37.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0012.1.37.out"
Args="--sample-id ee_ttbar_epmum_LR100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 12 --seed 365252012 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in"

ProcId=38
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0013.1.38.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0013.1.38.out"
Args="--sample-id ee_ttbar_epmum_LR100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 13 --seed 365252013 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in"

ProcId=39
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0014.1.39.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0014.1.39.out"
Args="--sample-id ee_ttbar_epmum_LR100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 14 --seed 365252014 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in"

ProcId=40
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0015.1.40.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0015.1.40.out"
Args="--sample-id ee_ttbar_epmum_LR100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 15 --seed 365252015 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in"

ProcId=41
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0016.1.41.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0016.1.41.out"
Args="--sample-id ee_ttbar_epmum_LR100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 16 --seed 365252016 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in"

ProcId=42
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0017.1.42.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0017.1.42.out"
Args="--sample-id ee_ttbar_epmum_LR100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 17 --seed 365252017 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in"

ProcId=43
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0018.1.43.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0018.1.43.out"
Args="--sample-id ee_ttbar_epmum_LR100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 18 --seed 365252018 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in"

ProcId=44
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0019.1.44.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0019.1.44.out"
Args="--sample-id ee_ttbar_epmum_LR100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 19 --seed 365252019 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in"

ProcId=45
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0020.1.45.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0020.1.45.out"
Args="--sample-id ee_ttbar_epmum_LR100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 20 --seed 365252020 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in"

ProcId=46
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0021.1.46.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0021.1.46.out"
Args="--sample-id ee_ttbar_epmum_LR100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 21 --seed 365252021 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in"

ProcId=47
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0022.1.47.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0022.1.47.out"
Args="--sample-id ee_ttbar_epmum_LR100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 22 --seed 365252022 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in"

ProcId=48
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0023.1.48.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0023.1.48.out"
Args="--sample-id ee_ttbar_epmum_LR100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 23 --seed 365252023 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in"

ProcId=49
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0024.1.49.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_LR100_iso_ISR_365GeV/shard_0024.1.49.out"
Args="--sample-id ee_ttbar_epmum_LR100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization LR100 --shard-index 24 --seed 365252024 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_LR100_iso_ISR_365GeV.sin.in"

ProcId=50
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0000.1.50.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0000.1.50.out"
Args="--sample-id ee_ttbar_epmum_RL100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 0 --seed 365253000 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in"

ProcId=51
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0001.1.51.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0001.1.51.out"
Args="--sample-id ee_ttbar_epmum_RL100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 1 --seed 365253001 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in"

ProcId=52
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0002.1.52.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0002.1.52.out"
Args="--sample-id ee_ttbar_epmum_RL100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 2 --seed 365253002 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in"

ProcId=53
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0003.1.53.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0003.1.53.out"
Args="--sample-id ee_ttbar_epmum_RL100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 3 --seed 365253003 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in"

ProcId=54
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0004.1.54.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0004.1.54.out"
Args="--sample-id ee_ttbar_epmum_RL100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 4 --seed 365253004 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in"

ProcId=55
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0005.1.55.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0005.1.55.out"
Args="--sample-id ee_ttbar_epmum_RL100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 5 --seed 365253005 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in"

ProcId=56
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0006.1.56.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0006.1.56.out"
Args="--sample-id ee_ttbar_epmum_RL100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 6 --seed 365253006 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in"

ProcId=57
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0007.1.57.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0007.1.57.out"
Args="--sample-id ee_ttbar_epmum_RL100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 7 --seed 365253007 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in"

ProcId=58
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0008.1.58.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0008.1.58.out"
Args="--sample-id ee_ttbar_epmum_RL100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 8 --seed 365253008 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in"

ProcId=59
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0009.1.59.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0009.1.59.out"
Args="--sample-id ee_ttbar_epmum_RL100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 9 --seed 365253009 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in"

ProcId=60
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0010.1.60.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0010.1.60.out"
Args="--sample-id ee_ttbar_epmum_RL100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 10 --seed 365253010 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in"

ProcId=61
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0011.1.61.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0011.1.61.out"
Args="--sample-id ee_ttbar_epmum_RL100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 11 --seed 365253011 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in"

ProcId=62
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0012.1.62.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0012.1.62.out"
Args="--sample-id ee_ttbar_epmum_RL100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 12 --seed 365253012 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in"

ProcId=63
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0013.1.63.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0013.1.63.out"
Args="--sample-id ee_ttbar_epmum_RL100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 13 --seed 365253013 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in"

ProcId=64
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0014.1.64.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0014.1.64.out"
Args="--sample-id ee_ttbar_epmum_RL100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 14 --seed 365253014 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in"

ProcId=65
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0015.1.65.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0015.1.65.out"
Args="--sample-id ee_ttbar_epmum_RL100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 15 --seed 365253015 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in"

ProcId=66
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0016.1.66.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0016.1.66.out"
Args="--sample-id ee_ttbar_epmum_RL100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 16 --seed 365253016 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in"

ProcId=67
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0017.1.67.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0017.1.67.out"
Args="--sample-id ee_ttbar_epmum_RL100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 17 --seed 365253017 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in"

ProcId=68
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0018.1.68.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0018.1.68.out"
Args="--sample-id ee_ttbar_epmum_RL100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 18 --seed 365253018 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in"

ProcId=69
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0019.1.69.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0019.1.69.out"
Args="--sample-id ee_ttbar_epmum_RL100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 19 --seed 365253019 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in"

ProcId=70
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0020.1.70.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0020.1.70.out"
Args="--sample-id ee_ttbar_epmum_RL100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 20 --seed 365253020 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in"

ProcId=71
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0021.1.71.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0021.1.71.out"
Args="--sample-id ee_ttbar_epmum_RL100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 21 --seed 365253021 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in"

ProcId=72
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0022.1.72.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0022.1.72.out"
Args="--sample-id ee_ttbar_epmum_RL100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 22 --seed 365253022 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in"

ProcId=73
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0023.1.73.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0023.1.73.out"
Args="--sample-id ee_ttbar_epmum_RL100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 23 --seed 365253023 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in"

ProcId=74
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0024.1.74.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_sc_ISR_365GeV/shard_0024.1.74.out"
Args="--sample-id ee_ttbar_epmum_RL100_sc_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 24 --seed 365253024 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_sc_ISR_365GeV.sin.in"

ProcId=75
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0000.1.75.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0000.1.75.out"
Args="--sample-id ee_ttbar_epmum_RL100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 0 --seed 365254000 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in"

ProcId=76
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0001.1.76.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0001.1.76.out"
Args="--sample-id ee_ttbar_epmum_RL100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 1 --seed 365254001 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in"

ProcId=77
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0002.1.77.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0002.1.77.out"
Args="--sample-id ee_ttbar_epmum_RL100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 2 --seed 365254002 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in"

ProcId=78
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0003.1.78.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0003.1.78.out"
Args="--sample-id ee_ttbar_epmum_RL100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 3 --seed 365254003 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in"

ProcId=79
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0004.1.79.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0004.1.79.out"
Args="--sample-id ee_ttbar_epmum_RL100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 4 --seed 365254004 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in"

ProcId=80
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0005.1.80.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0005.1.80.out"
Args="--sample-id ee_ttbar_epmum_RL100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 5 --seed 365254005 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in"

ProcId=81
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0006.1.81.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0006.1.81.out"
Args="--sample-id ee_ttbar_epmum_RL100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 6 --seed 365254006 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in"

ProcId=82
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0007.1.82.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0007.1.82.out"
Args="--sample-id ee_ttbar_epmum_RL100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 7 --seed 365254007 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in"

ProcId=83
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0008.1.83.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0008.1.83.out"
Args="--sample-id ee_ttbar_epmum_RL100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 8 --seed 365254008 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in"

ProcId=84
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0009.1.84.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0009.1.84.out"
Args="--sample-id ee_ttbar_epmum_RL100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 9 --seed 365254009 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in"

ProcId=85
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0010.1.85.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0010.1.85.out"
Args="--sample-id ee_ttbar_epmum_RL100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 10 --seed 365254010 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in"

ProcId=86
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0011.1.86.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0011.1.86.out"
Args="--sample-id ee_ttbar_epmum_RL100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 11 --seed 365254011 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in"

ProcId=87
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0012.1.87.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0012.1.87.out"
Args="--sample-id ee_ttbar_epmum_RL100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 12 --seed 365254012 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in"

ProcId=88
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0013.1.88.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0013.1.88.out"
Args="--sample-id ee_ttbar_epmum_RL100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 13 --seed 365254013 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in"

ProcId=89
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0014.1.89.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0014.1.89.out"
Args="--sample-id ee_ttbar_epmum_RL100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 14 --seed 365254014 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in"

ProcId=90
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0015.1.90.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0015.1.90.out"
Args="--sample-id ee_ttbar_epmum_RL100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 15 --seed 365254015 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in"

ProcId=91
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0016.1.91.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0016.1.91.out"
Args="--sample-id ee_ttbar_epmum_RL100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 16 --seed 365254016 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in"

ProcId=92
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0017.1.92.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0017.1.92.out"
Args="--sample-id ee_ttbar_epmum_RL100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 17 --seed 365254017 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in"

ProcId=93
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0018.1.93.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0018.1.93.out"
Args="--sample-id ee_ttbar_epmum_RL100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 18 --seed 365254018 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in"

ProcId=94
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0019.1.94.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0019.1.94.out"
Args="--sample-id ee_ttbar_epmum_RL100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 19 --seed 365254019 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in"

ProcId=95
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0020.1.95.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0020.1.95.out"
Args="--sample-id ee_ttbar_epmum_RL100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 20 --seed 365254020 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in"

ProcId=96
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0021.1.96.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0021.1.96.out"
Args="--sample-id ee_ttbar_epmum_RL100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 21 --seed 365254021 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in"

ProcId=97
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0022.1.97.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0022.1.97.out"
Args="--sample-id ee_ttbar_epmum_RL100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 22 --seed 365254022 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in"

ProcId=98
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0023.1.98.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0023.1.98.out"
Args="--sample-id ee_ttbar_epmum_RL100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 23 --seed 365254023 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in"

ProcId=99
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0024.1.99.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_epmum_RL100_iso_ISR_365GeV/shard_0024.1.99.out"
Args="--sample-id ee_ttbar_epmum_RL100_iso_ISR_365GeV --initial-state ee --decay-channel epmum --polarization RL100 --shard-index 24 --seed 365254024 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_epmum_RL100_iso_ISR_365GeV.sin.in"

ProcId=100
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0000.1.100.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0000.1.100.out"
Args="--sample-id ee_ttbar_mupem_LR100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 0 --seed 365255000 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in"

ProcId=101
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0001.1.101.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0001.1.101.out"
Args="--sample-id ee_ttbar_mupem_LR100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 1 --seed 365255001 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in"

ProcId=102
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0002.1.102.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0002.1.102.out"
Args="--sample-id ee_ttbar_mupem_LR100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 2 --seed 365255002 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in"

ProcId=103
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0003.1.103.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0003.1.103.out"
Args="--sample-id ee_ttbar_mupem_LR100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 3 --seed 365255003 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in"

ProcId=104
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0004.1.104.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0004.1.104.out"
Args="--sample-id ee_ttbar_mupem_LR100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 4 --seed 365255004 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in"

ProcId=105
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0005.1.105.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0005.1.105.out"
Args="--sample-id ee_ttbar_mupem_LR100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 5 --seed 365255005 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in"

ProcId=106
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0006.1.106.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0006.1.106.out"
Args="--sample-id ee_ttbar_mupem_LR100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 6 --seed 365255006 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in"

ProcId=107
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0007.1.107.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0007.1.107.out"
Args="--sample-id ee_ttbar_mupem_LR100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 7 --seed 365255007 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in"

ProcId=108
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0008.1.108.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0008.1.108.out"
Args="--sample-id ee_ttbar_mupem_LR100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 8 --seed 365255008 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in"

ProcId=109
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0009.1.109.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0009.1.109.out"
Args="--sample-id ee_ttbar_mupem_LR100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 9 --seed 365255009 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in"

ProcId=110
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0010.1.110.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0010.1.110.out"
Args="--sample-id ee_ttbar_mupem_LR100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 10 --seed 365255010 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in"

ProcId=111
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0011.1.111.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0011.1.111.out"
Args="--sample-id ee_ttbar_mupem_LR100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 11 --seed 365255011 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in"

ProcId=112
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0012.1.112.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0012.1.112.out"
Args="--sample-id ee_ttbar_mupem_LR100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 12 --seed 365255012 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in"

ProcId=113
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0013.1.113.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0013.1.113.out"
Args="--sample-id ee_ttbar_mupem_LR100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 13 --seed 365255013 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in"

ProcId=114
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0014.1.114.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0014.1.114.out"
Args="--sample-id ee_ttbar_mupem_LR100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 14 --seed 365255014 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in"

ProcId=115
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0015.1.115.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0015.1.115.out"
Args="--sample-id ee_ttbar_mupem_LR100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 15 --seed 365255015 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in"

ProcId=116
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0016.1.116.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0016.1.116.out"
Args="--sample-id ee_ttbar_mupem_LR100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 16 --seed 365255016 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in"

ProcId=117
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0017.1.117.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0017.1.117.out"
Args="--sample-id ee_ttbar_mupem_LR100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 17 --seed 365255017 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in"

ProcId=118
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0018.1.118.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0018.1.118.out"
Args="--sample-id ee_ttbar_mupem_LR100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 18 --seed 365255018 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in"

ProcId=119
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0019.1.119.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0019.1.119.out"
Args="--sample-id ee_ttbar_mupem_LR100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 19 --seed 365255019 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in"

ProcId=120
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0020.1.120.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0020.1.120.out"
Args="--sample-id ee_ttbar_mupem_LR100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 20 --seed 365255020 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in"

ProcId=121
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0021.1.121.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0021.1.121.out"
Args="--sample-id ee_ttbar_mupem_LR100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 21 --seed 365255021 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in"

ProcId=122
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0022.1.122.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0022.1.122.out"
Args="--sample-id ee_ttbar_mupem_LR100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 22 --seed 365255022 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in"

ProcId=123
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0023.1.123.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0023.1.123.out"
Args="--sample-id ee_ttbar_mupem_LR100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 23 --seed 365255023 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in"

ProcId=124
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0024.1.124.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_sc_ISR_365GeV/shard_0024.1.124.out"
Args="--sample-id ee_ttbar_mupem_LR100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 24 --seed 365255024 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_sc_ISR_365GeV.sin.in"

ProcId=125
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0000.1.125.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0000.1.125.out"
Args="--sample-id ee_ttbar_mupem_LR100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 0 --seed 365256000 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in"

ProcId=126
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0001.1.126.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0001.1.126.out"
Args="--sample-id ee_ttbar_mupem_LR100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 1 --seed 365256001 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in"

ProcId=127
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0002.1.127.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0002.1.127.out"
Args="--sample-id ee_ttbar_mupem_LR100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 2 --seed 365256002 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in"

ProcId=128
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0003.1.128.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0003.1.128.out"
Args="--sample-id ee_ttbar_mupem_LR100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 3 --seed 365256003 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in"

ProcId=129
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0004.1.129.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0004.1.129.out"
Args="--sample-id ee_ttbar_mupem_LR100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 4 --seed 365256004 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in"

ProcId=130
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0005.1.130.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0005.1.130.out"
Args="--sample-id ee_ttbar_mupem_LR100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 5 --seed 365256005 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in"

ProcId=131
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0006.1.131.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0006.1.131.out"
Args="--sample-id ee_ttbar_mupem_LR100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 6 --seed 365256006 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in"

ProcId=132
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0007.1.132.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0007.1.132.out"
Args="--sample-id ee_ttbar_mupem_LR100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 7 --seed 365256007 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in"

ProcId=133
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0008.1.133.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0008.1.133.out"
Args="--sample-id ee_ttbar_mupem_LR100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 8 --seed 365256008 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in"

ProcId=134
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0009.1.134.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0009.1.134.out"
Args="--sample-id ee_ttbar_mupem_LR100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 9 --seed 365256009 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in"

ProcId=135
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0010.1.135.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0010.1.135.out"
Args="--sample-id ee_ttbar_mupem_LR100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 10 --seed 365256010 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in"

ProcId=136
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0011.1.136.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0011.1.136.out"
Args="--sample-id ee_ttbar_mupem_LR100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 11 --seed 365256011 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in"

ProcId=137
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0012.1.137.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0012.1.137.out"
Args="--sample-id ee_ttbar_mupem_LR100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 12 --seed 365256012 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in"

ProcId=138
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0013.1.138.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0013.1.138.out"
Args="--sample-id ee_ttbar_mupem_LR100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 13 --seed 365256013 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in"

ProcId=139
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0014.1.139.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0014.1.139.out"
Args="--sample-id ee_ttbar_mupem_LR100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 14 --seed 365256014 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in"

ProcId=140
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0015.1.140.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0015.1.140.out"
Args="--sample-id ee_ttbar_mupem_LR100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 15 --seed 365256015 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in"

ProcId=141
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0016.1.141.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0016.1.141.out"
Args="--sample-id ee_ttbar_mupem_LR100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 16 --seed 365256016 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in"

ProcId=142
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0017.1.142.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0017.1.142.out"
Args="--sample-id ee_ttbar_mupem_LR100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 17 --seed 365256017 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in"

ProcId=143
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0018.1.143.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0018.1.143.out"
Args="--sample-id ee_ttbar_mupem_LR100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 18 --seed 365256018 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in"

ProcId=144
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0019.1.144.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0019.1.144.out"
Args="--sample-id ee_ttbar_mupem_LR100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 19 --seed 365256019 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in"

ProcId=145
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0020.1.145.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0020.1.145.out"
Args="--sample-id ee_ttbar_mupem_LR100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 20 --seed 365256020 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in"

ProcId=146
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0021.1.146.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0021.1.146.out"
Args="--sample-id ee_ttbar_mupem_LR100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 21 --seed 365256021 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in"

ProcId=147
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0022.1.147.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0022.1.147.out"
Args="--sample-id ee_ttbar_mupem_LR100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 22 --seed 365256022 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in"

ProcId=148
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0023.1.148.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0023.1.148.out"
Args="--sample-id ee_ttbar_mupem_LR100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 23 --seed 365256023 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in"

ProcId=149
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0024.1.149.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_LR100_iso_ISR_365GeV/shard_0024.1.149.out"
Args="--sample-id ee_ttbar_mupem_LR100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization LR100 --shard-index 24 --seed 365256024 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_LR100_iso_ISR_365GeV.sin.in"

ProcId=150
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0000.1.150.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0000.1.150.out"
Args="--sample-id ee_ttbar_mupem_RL100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 0 --seed 365257000 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in"

ProcId=151
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0001.1.151.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0001.1.151.out"
Args="--sample-id ee_ttbar_mupem_RL100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 1 --seed 365257001 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in"

ProcId=152
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0002.1.152.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0002.1.152.out"
Args="--sample-id ee_ttbar_mupem_RL100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 2 --seed 365257002 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in"

ProcId=153
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0003.1.153.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0003.1.153.out"
Args="--sample-id ee_ttbar_mupem_RL100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 3 --seed 365257003 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in"

ProcId=154
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0004.1.154.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0004.1.154.out"
Args="--sample-id ee_ttbar_mupem_RL100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 4 --seed 365257004 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in"

ProcId=155
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0005.1.155.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0005.1.155.out"
Args="--sample-id ee_ttbar_mupem_RL100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 5 --seed 365257005 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in"

ProcId=156
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0006.1.156.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0006.1.156.out"
Args="--sample-id ee_ttbar_mupem_RL100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 6 --seed 365257006 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in"

ProcId=157
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0007.1.157.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0007.1.157.out"
Args="--sample-id ee_ttbar_mupem_RL100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 7 --seed 365257007 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in"

ProcId=158
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0008.1.158.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0008.1.158.out"
Args="--sample-id ee_ttbar_mupem_RL100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 8 --seed 365257008 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in"

ProcId=159
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0009.1.159.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0009.1.159.out"
Args="--sample-id ee_ttbar_mupem_RL100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 9 --seed 365257009 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in"

ProcId=160
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0010.1.160.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0010.1.160.out"
Args="--sample-id ee_ttbar_mupem_RL100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 10 --seed 365257010 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in"

ProcId=161
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0011.1.161.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0011.1.161.out"
Args="--sample-id ee_ttbar_mupem_RL100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 11 --seed 365257011 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in"

ProcId=162
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0012.1.162.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0012.1.162.out"
Args="--sample-id ee_ttbar_mupem_RL100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 12 --seed 365257012 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in"

ProcId=163
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0013.1.163.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0013.1.163.out"
Args="--sample-id ee_ttbar_mupem_RL100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 13 --seed 365257013 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in"

ProcId=164
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0014.1.164.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0014.1.164.out"
Args="--sample-id ee_ttbar_mupem_RL100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 14 --seed 365257014 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in"

ProcId=165
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0015.1.165.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0015.1.165.out"
Args="--sample-id ee_ttbar_mupem_RL100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 15 --seed 365257015 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in"

ProcId=166
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0016.1.166.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0016.1.166.out"
Args="--sample-id ee_ttbar_mupem_RL100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 16 --seed 365257016 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in"

ProcId=167
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0017.1.167.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0017.1.167.out"
Args="--sample-id ee_ttbar_mupem_RL100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 17 --seed 365257017 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in"

ProcId=168
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0018.1.168.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0018.1.168.out"
Args="--sample-id ee_ttbar_mupem_RL100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 18 --seed 365257018 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in"

ProcId=169
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0019.1.169.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0019.1.169.out"
Args="--sample-id ee_ttbar_mupem_RL100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 19 --seed 365257019 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in"

ProcId=170
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0020.1.170.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0020.1.170.out"
Args="--sample-id ee_ttbar_mupem_RL100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 20 --seed 365257020 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in"

ProcId=171
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0021.1.171.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0021.1.171.out"
Args="--sample-id ee_ttbar_mupem_RL100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 21 --seed 365257021 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in"

ProcId=172
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0022.1.172.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0022.1.172.out"
Args="--sample-id ee_ttbar_mupem_RL100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 22 --seed 365257022 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in"

ProcId=173
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0023.1.173.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0023.1.173.out"
Args="--sample-id ee_ttbar_mupem_RL100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 23 --seed 365257023 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in"

ProcId=174
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0024.1.174.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_sc_ISR_365GeV/shard_0024.1.174.out"
Args="--sample-id ee_ttbar_mupem_RL100_sc_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 24 --seed 365257024 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_sc_ISR_365GeV.sin.in"

ProcId=175
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0000.1.175.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0000.1.175.out"
Args="--sample-id ee_ttbar_mupem_RL100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 0 --seed 365258000 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in"

ProcId=176
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0001.1.176.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0001.1.176.out"
Args="--sample-id ee_ttbar_mupem_RL100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 1 --seed 365258001 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in"

ProcId=177
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0002.1.177.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0002.1.177.out"
Args="--sample-id ee_ttbar_mupem_RL100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 2 --seed 365258002 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in"

ProcId=178
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0003.1.178.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0003.1.178.out"
Args="--sample-id ee_ttbar_mupem_RL100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 3 --seed 365258003 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in"

ProcId=179
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0004.1.179.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0004.1.179.out"
Args="--sample-id ee_ttbar_mupem_RL100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 4 --seed 365258004 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in"

ProcId=180
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0005.1.180.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0005.1.180.out"
Args="--sample-id ee_ttbar_mupem_RL100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 5 --seed 365258005 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in"

ProcId=181
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0006.1.181.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0006.1.181.out"
Args="--sample-id ee_ttbar_mupem_RL100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 6 --seed 365258006 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in"

ProcId=182
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0007.1.182.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0007.1.182.out"
Args="--sample-id ee_ttbar_mupem_RL100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 7 --seed 365258007 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in"

ProcId=183
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0008.1.183.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0008.1.183.out"
Args="--sample-id ee_ttbar_mupem_RL100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 8 --seed 365258008 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in"

ProcId=184
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0009.1.184.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0009.1.184.out"
Args="--sample-id ee_ttbar_mupem_RL100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 9 --seed 365258009 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in"

ProcId=185
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0010.1.185.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0010.1.185.out"
Args="--sample-id ee_ttbar_mupem_RL100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 10 --seed 365258010 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in"

ProcId=186
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0011.1.186.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0011.1.186.out"
Args="--sample-id ee_ttbar_mupem_RL100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 11 --seed 365258011 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in"

ProcId=187
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0012.1.187.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0012.1.187.out"
Args="--sample-id ee_ttbar_mupem_RL100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 12 --seed 365258012 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in"

ProcId=188
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0013.1.188.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0013.1.188.out"
Args="--sample-id ee_ttbar_mupem_RL100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 13 --seed 365258013 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in"

ProcId=189
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0014.1.189.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0014.1.189.out"
Args="--sample-id ee_ttbar_mupem_RL100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 14 --seed 365258014 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in"

ProcId=190
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0015.1.190.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0015.1.190.out"
Args="--sample-id ee_ttbar_mupem_RL100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 15 --seed 365258015 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in"

ProcId=191
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0016.1.191.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0016.1.191.out"
Args="--sample-id ee_ttbar_mupem_RL100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 16 --seed 365258016 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in"

ProcId=192
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0017.1.192.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0017.1.192.out"
Args="--sample-id ee_ttbar_mupem_RL100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 17 --seed 365258017 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in"

ProcId=193
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0018.1.193.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0018.1.193.out"
Args="--sample-id ee_ttbar_mupem_RL100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 18 --seed 365258018 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in"

ProcId=194
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0019.1.194.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0019.1.194.out"
Args="--sample-id ee_ttbar_mupem_RL100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 19 --seed 365258019 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in"

ProcId=195
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0020.1.195.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0020.1.195.out"
Args="--sample-id ee_ttbar_mupem_RL100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 20 --seed 365258020 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in"

ProcId=196
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0021.1.196.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0021.1.196.out"
Args="--sample-id ee_ttbar_mupem_RL100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 21 --seed 365258021 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in"

ProcId=197
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0022.1.197.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0022.1.197.out"
Args="--sample-id ee_ttbar_mupem_RL100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 22 --seed 365258022 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in"

ProcId=198
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0023.1.198.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0023.1.198.out"
Args="--sample-id ee_ttbar_mupem_RL100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 23 --seed 365258023 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in"

ProcId=199
JobStatus=1
Err="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stderr/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0024.1.199.err"
Out="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/condor/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1/full/paper_spin_365GeV_ee_lhe_matrix_250k_v1/20260727T161351Z/stdout/ee_ttbar_mupem_RL100_iso_ISR_365GeV/shard_0024.1.199.out"
Args="--sample-id ee_ttbar_mupem_RL100_iso_ISR_365GeV --initial-state ee --decay-channel mupem --polarization RL100 --shard-index 24 --seed 365258024 --events 10000 --campaign-root /eos/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/production/paper_spin_365GeV_ee_lhe_matrix_250k_v1 --template ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in --archive-workspace 1 --no-force"
TransferInput="/afs/cern.ch/user/c/cglenn/FCCWork/whizard/whizard_ttbar_spinpol/sindarin/generated/paper_spin_365GeV_ee_lhe_matrix_250k_v1/ee_ttbar_mupem_RL100_iso_ISR_365GeV.sin.in"
