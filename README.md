[TITLE]

Schedule 1 Strain Renamer (EXE GUI Tool for Windows)

[SHORT DESCRIPTION]

Easily rename drug strains (products) in your Schedule 1 save files with this user-friendly GUI tool (standalone Windows executable). No Python needed! Features automatic save detection, backups, single and bulk renaming.

[LONG DESCRIPTION]

Tired of the default strain names in Schedule 1? Want to add your own custom names or organize your product list? This tool provides a simple graphical interface (GUI) to rename the drug strains (referred to as "Products" in the save files) discovered in your game.

This is a standalone Windows executable – **no need to install Python!** Just download and run.

It automatically finds your save files, creates backups before making changes, and allows you to rename strains individually or in bulk.

[FEATURES]

*   **Standalone Executable:** No need to install Python or any dependencies. Just download and run on Windows.
*   **Automatic Save Detection:** Finds your Schedule 1 save folders on Windows automatically. Also allows manual browsing.
*   **Automatic Backups:** Creates a timestamped backup copy of your save folder before any modifications are made, ensuring you can revert if something goes wrong.
*   **Product Lister:** Displays a clear, sortable, and filterable list of all your discovered strains, showing their internal ID, current display name, type, and properties.
*   **Single Rename:** Easily select a strain and give it a new name. The tool intelligently updates both the display name and the internal ID (automatically generated from the new name) across all necessary parts of your save file.
*   **Bulk Rename:** Rename multiple strains at once using a simple text input. Just provide lines in the format: `original_id,new_name`. The tool handles generating unique new IDs based on the names provided.
*   **Import/Export Bulk List:** Import rename lists from CSV or TXT files, or export your current list for backup or sharing.
*   **User-Friendly GUI:** Simple tabbed interface built with Tkinter.

[HOW TO USE]

1.  **Download:** Download the `Schedule1StrainRenamer.exe` file. It's recommended to place it in its own folder or on your Desktop.
2.  **Run the Tool:** Double-click the `Schedule1StrainRenamer.exe` file to launch the application. (Windows Defender or other antivirus might show a warning the first time – this can happen with compiled Python scripts. You may need to allow it to run).
3.  **Select Save:** The tool should automatically detect your save(s). Select the one you want to modify from the dropdown menu. If it doesn't find it, use the "Browse..." button to locate your save folder manually (it's the folder containing `Products.json`).
4.  **View Products:** Use the "Product List" tab to see all your current strains. You can filter and sort the list.
5.  **Rename:**
    *   **Single:** Go to the "Rename" tab, select the "Product ID" you want to change, enter the "New Name", and click "Rename".
    *   **Bulk:** Go to the "Bulk Rename" tab. Enter your renames using the `original_id,new_name` format (one per line), or import a CSV/TXT file. Click "Apply Changes".
6.  **Backup Created:** A backup of your save folder (e.g., `save_backup_YYYYMMDD_HHMMSS`) will be created in the same location as your original save folder *before* changes are applied.
7.  **Load Game:** Close the tool and launch Schedule 1 to see your renamed strains!

[IMPORTANT NOTES & WARNINGS]

*   **[color=#FF0000]BACKUP YOUR SAVES MANUALLY![/color]** While this tool includes an automatic backup feature, it is [b]STRONGLY RECOMMENDED[/b] that you make your own separate, manual backup of your save folder before using this or *any* save editing tool. The save file location on Windows is:
    *   `%USERPROFILE%\AppData\LocalLow\TVGS\Schedule I\Saves\<YourSteamID>\SaveGame_X`
*   **ID Generation:** When renaming (single or bulk), the tool generates a new internal ID based on the new name you provide (it converts the name to lowercase and removes non-alphanumeric characters). If this generated ID already exists, it will append a number to ensure uniqueness. This ensures compatibility within the game's systems.
*   **Windows Only:** This executable version is specifically for Windows.
*   **Antivirus Warnings:** Some antivirus programs may flag applications created from Python scripts (like this one) as potentially suspicious, especially if they aren't digitally signed. This is often a false positive. If you downloaded the tool from a trusted source (like NexusMods), you can usually safely allow it.
*   **Game Updates:** This tool modifies save files directly. Future updates to Schedule 1 *could* potentially change the save format and break compatibility. Use at your own risk after game updates until confirmed compatible.

[REQUIREMENTS]

*   Windows (Tested on Windows 10/11, should work on recent versions)
