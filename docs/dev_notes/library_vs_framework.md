
This doc is supposed to clarify how commands run under `argrelay` work<br/>
via side-by-side comparison of (independent) `argparse` _library_ and `argrelay` _framework_.

```mermaid
graph RL;

    %% user --> library
    %% user --> framework

    subgraph `argparse` library

        direction LR

        some.py <--> argparse;

    end

    argrelay_client -. delegates = relays .-> some.py;

    subgraph `argrelay` framework

        direction TB

        subgraph client

            direction LR

            relay2some --> argrelay_client[argrelay client];

        end

        subgraph server

            direction TB

            argrelay_server[argrelay server] <--> data[(data)];

        end

    end

```

| Category       | `argparse` is a library                                    | `argrelay` is a framework                                                      |
|:---------------|:-----------------------------------------------------------|:-------------------------------------------------------------------------------|
| Given:         | `some.py` is some script                                   | `relay2some` is a "wrapper" command<br/> configured in Bash to call `argrelay` |
| In Bash:       | type `some.py` to execute it                               | type `relay2some` to let `argrelay` decide<br/> whether to execute `some.py`   |
| Execution:     | `some.py` calls `argparse` library                         | `some.py` is called by the framework<br/> when `relay2some` is invoked         |
| Function:      | `some.py` directly does<br/> domain-specific task          | `relay2some` directly only "relays"<br/> the command line to `argrelay`        |
| CLI source:    | `some.py` defines its CLI<br/> itself via `argparse`       | CLI for `relay2some` is defined by<br/> the framework via configs/plugins/data |
| CLI is:        | mostly code-driven                                         | mostly data-driven                                                             |
| Modify CLI:    | modify `some.py`                                           | keep `some.py` intact,<br/> re-configure `argrelay` instead                    |
| Prog lang:     | `some.py` has to be<br/> a Python script to use `argparse` | `some.py` can be anything<br/> somehow executable by `argrelay`                |
| **Important:** | `some.py`/`argparse` have<br/> no domain data to query     | `relay2some` may access any<br/> domain data from `argrelay` server            |

