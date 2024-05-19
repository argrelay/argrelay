
This doc is an (incomplete and outdated) attempt to list next steps as a tutorial.

<a name="argrelay-next-steps"></a>
# What's next?

*   Modify [`ServiceLoader.py` plugin][link_to_load_data_envelopes] to provide data beyond [demo data set][TD_63_37_05_36.demo_services_data.md].

    The data can be simply hard-coded with different `test_data` tag<br/>
    (other than `TD_63_37_05_36` demo) and selected in `argrelay_server.yaml`:

    ```diff
        ServiceLoader:
            plugin_module_name: argrelay.custom_integ.ServiceLoader
            plugin_class_name: ServiceLoader
            plugin_config:
                test_data_ids_to_load:
                    #-   TD_70_69_38_46  # no data
    -               -   TD_63_37_05_36  # demo
    +               -   TD_NN_NN_NN_NN  # custom data
                    #-   TD_38_03_48_51  # large generated
    ```

    If hard-coding is boring, soft-code to load it from external data source.

*   Replace [redirect to `ErrorDelegator.py` plugin][link_to_redirect_to_error]<br/>
    to execute something useful instead when use hits `Enter`.

*   ...

[TD_63_37_05_36.demo_services_data.md]: docs/test_data/TD_63_37_05_36.demo_services_data.md
[link_to_redirect_to_error]: https://github.com/argrelay/argrelay/blob/v0.0.0.dev27/src/argrelay/custom_integ/ServiceInvocator.py#L148
[link_to_load_data_envelopes]: https://github.com/argrelay/argrelay/blob/v0.0.0.dev27/src/argrelay/custom_integ/ServiceLoader.py#L111
