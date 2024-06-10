*** Settings ***
Library    ConfigManager.py
Library    Collections
Library    BuiltIn

*** Variables ***
${SOURCE_PATH}    /path/to/source

*** Test Cases ***
Create And Verify Config Structure
    Create Config Manager Instance
    Create Directory Structure    sk_1    sk_2    sk_3
    Load Config    ${SOURCE_PATH}
    Copy Files

*** Keywords ***
Create Config Manager Instance
    ${manager}=    Evaluate    ConfigManager.ConfigManager()    modules=ConfigManager
    Set Suite Variable    ${manager}

Create Directory Structure
    [Arguments]    @{subfolders}
    Call Method    ${manager}    create_directory_structure    ${subfolders}

Load Config
    [Arguments]    ${source_path}
    Call Method    ${manager}    load_config    ${source_path}

Copy Files
    Call Method    ${manager}    copy_files
