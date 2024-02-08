This is a fork of Nayfach and Pollard's tool MicrobeCensus.

A `TypeError` was created in the `check_rapsearch()` subroutine of `run_pipeline()` by a recent version of Python. This has been fixed in this fork so that the tool can be deployed in SourceApp as part of a combined `conda`/`mamba` environment with other tools using newer versions of Python. 

For the official version, see:

https://github.com/snayfach/MicrobeCensus

And the context of its deployment in SourceApp:

https://github.com/blindner6/SourceApp
