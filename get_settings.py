def get_settings():
    """Return the settings in a dict."""
    with open("settings.cfg", "r") as f:
        string = f.readlines()

    settings = {}
    for line in string:
        try:
            key, value = line.replace(" ", "").replace("\n", "").split(":")
        except ValueError:
            continue
        value = value.split("//")[0]
        
        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                if "(" in value and ")" in value:
                    value = value.replace("(", "").replace(")", "")
                    value = value.split(",")

                    val_list = []
                    for val in value:
                        try:
                            val = int(val)
                        except ValueError:
                            val = float(val)

                        val_list.append(val)

                    value = val_list
                else:
                    if value.lower() == "true":
                        value = True
                    elif value.lower() == "false":
                        value = False

        settings[key] = value

    return settings
