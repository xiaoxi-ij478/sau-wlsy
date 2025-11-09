try:
    from . import globals as globals_module

except ImportError:
    import sys
    import os.path

    # stolen from yt-dlp
    sys.path.insert(
        0,
        os.path.dirname(
            os.path.dirname(
                os.path.realpath(
                    os.path.abspath(
                        __file__
                    )
                )
            )
        )
    )

    import wlsy.globals as globals_module

globals_module.login_activate()
globals_module.root.mainloop()
