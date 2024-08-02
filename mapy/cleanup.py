import os
import tempfile
import threading

from datetime import datetime, timedelta


def schedule_tempfile_cleanup(interval_hours=1, max_file_age_hours=1):
    """
    Schedules a periodic cleanup of temporary files created during the attachment download process.

    :param interval_hours: The interval in hours between cleanup runs.
    :param max_file_age_hours: The maximum age in hours for temporary files before they are deleted.
    """

    def cleanup():
        while True:
            print("Starting cleanup...")

            temp_dir = tempfile.gettempdir()
            current_time = datetime.now()

            # Use a specific prefix to identify files created by this app
            prefix = 'mapy_'

            for filename in os.listdir(temp_dir):
                if filename.startswith(prefix):
                    file_path = os.path.join(temp_dir, filename)

                    if os.path.isfile(file_path):
                        file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        file_age = current_time - file_mod_time

                        if file_age > timedelta(hours=max_file_age_hours):
                            try:
                                os.remove(file_path)
                                print(f"Deleted old temp file: {file_path}")
                            except Exception as e:
                                print(f"Error deleting file {file_path}: {e}")

            print("Cleanup done.")

            threading.Event().wait(interval_hours * 3600)

    # Start the cleanup process in a separate daemon thread
    cleanup_thread = threading.Thread(target=cleanup, daemon=True)
    cleanup_thread.start()
