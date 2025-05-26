import os
import zipfile
import logging
import glob
from datetime import datetime

# Configure logging
log_filename = f"nhs_zip_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

def find_nhs_documents(directories=None, patterns=None):
    """
    Find NHS funding scheme documents based on directories and file patterns.
    
    Args:
        directories (list): List of directories to search in. Defaults to current directory.
        patterns (list): List of file patterns to match. Defaults to common document types.
        
    Returns:
        list: List of file paths matching the criteria
    """
    if directories is None:
        directories = [os.getcwd()]  # Default to current directory
    
    if patterns is None:
        # Default patterns for NHS funding documents
        patterns = [
            "*.pdf", "*.docx", "*.xlsx", "*.pptx", "*.doc", 
            "*business*case*", "*proposal*", "*fund*", "*NHS*", 
            "*project*", "*PID*", "*initiation*"
        ]
    
    logging.info(f"Searching for NHS documents in {len(directories)} directories with {len(patterns)} patterns")
    
    documents = []
    for directory in directories:
        if not os.path.exists(directory):
            logging.warning(f"Directory does not exist: {directory}")
            continue
            
        for pattern in patterns:
            search_path = os.path.join(directory, "**", pattern)
            found_files = glob.glob(search_path, recursive=True)
            for file in found_files:
                if os.path.isfile(file) and file not in documents:
                    documents.append(file)
    
    logging.info(f"Found {len(documents)} potential NHS funding scheme documents")
    return documents

def create_nhs_project_zip(zip_filename, document_paths=None, source_directories=None, file_patterns=None):
    """
    Creates a ZIP archive containing NHS funding scheme project documents.

    Args:
        zip_filename (str): The name of the output ZIP file.
        document_paths (list, optional): A list of specific file paths to include.
        source_directories (list, optional): Directories to search for documents.
        file_patterns (list, optional): File patterns to match.
    
    Returns:
        bool: True if the ZIP was created successfully, False otherwise.
    """
    logging.info(f"Starting creation of NHS funding scheme ZIP archive: {zip_filename}")
    
    try:
        # If no specific documents provided, search for them
        if document_paths is None:
            document_paths = find_nhs_documents(source_directories, file_patterns)
            
        if not document_paths:
            logging.error("No documents found to archive")
            return False
            
        # Create directory for the zip file if it doesn't exist
        zip_dir = os.path.dirname(zip_filename)
        if zip_dir and not os.path.exists(zip_dir):
            try:
                os.makedirs(zip_dir)
                logging.info(f"Created directory: {zip_dir}")
            except Exception as e:
                logging.error(f"Failed to create directory {zip_dir}: {e}")
                return False
        
        # Create the ZIP file
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            successful_files = 0
            failed_files = 0
            
            for doc_path in document_paths:
                if os.path.exists(doc_path):
                    try:
                        # Add file to the zip archive
                        arcname = os.path.basename(doc_path)
                        zipf.write(doc_path, arcname)
                        logging.info(f"Added '{doc_path}' to archive as '{arcname}'")
                        successful_files += 1
                    except Exception as e:
                        logging.error(f"Error adding file '{doc_path}' to ZIP: {e}")
                        failed_files += 1
                else:
                    logging.warning(f"Document not found, skipping: '{doc_path}'")
                    failed_files += 1
            
        # Log summary
        total_files = successful_files + failed_files
        success_rate = (successful_files / total_files * 100) if total_files > 0 else 0
        logging.info(f"ZIP creation complete: {zip_filename}")
        logging.info(f"Summary: {successful_files} files added successfully, {failed_files} failed")
        logging.info(f"Success rate: {success_rate:.2f}%")
        
        # Verify the ZIP file exists and has content
        if os.path.exists(zip_filename) and os.path.getsize(zip_filename) > 0:
            logging.info(f"Successfully created ZIP archive: {zip_filename} ({os.path.getsize(zip_filename)} bytes)")
            return True
        else:
            logging.error(f"ZIP file was created but appears to be empty or invalid")
            return False

    except FileNotFoundError:
        logging.error(f"Error: Could not create ZIP file. Directory may not exist.")
    except PermissionError:
        logging.error(f"Error: Permission denied to create ZIP file: {zip_filename}")
    except zipfile.BadZipFile:
        logging.error(f"Error: The created file is not a valid ZIP file.")
    except Exception as e:
        logging.error(f"An unexpected error occurred during ZIP creation: {e}")
    
    return False

if __name__ == "__main__":
    # Define output ZIP filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_zip = f"NHS_FundingScheme_Documents_{timestamp}.zip"
    
    print("NHS Funding Scheme Documents ZIP Creator")
    print("----------------------------------------")
    print(f"Output ZIP file will be: {output_zip}")
    print()
    
    # Two options for running the script
    print("Options:")
    print("1. Auto-discover NHS funding documents in current directory")
    print("2. Auto-discover NHS funding documents in specific directories")
    print("3. Use a list of specific document paths")
    
    try:
        choice = input("Enter your choice (1-3): ")
        
        if choice == "1":
            # Option 1: Auto-discover in current directory
            success = create_nhs_project_zip(output_zip)
        
        elif choice == "2":
            # Option 2: Auto-discover in specific directories
            dir_input = input("Enter directories to search (comma-separated): ")
            directories = [d.strip() for d in dir_input.split(",")]
            
            patterns_input = input("Enter file patterns to match (comma-separated, leave empty for defaults): ")
            patterns = None
            if patterns_input.strip():
                patterns = [p.strip() for p in patterns_input.split(",")]
                
            success = create_nhs_project_zip(
                output_zip,
                source_directories=directories,
                file_patterns=patterns
            )
            
        elif choice == "3":
            # Option 3: Specific document paths
            docs_input = input("Enter document paths (comma-separated): ")
            documents = [d.strip() for d in docs_input.split(",")]
            
            success = create_nhs_project_zip(output_zip, document_paths=documents)
            
        else:
            print("Invalid choice. Exiting.")
            success = False
            
        if success:
            print(f"
ZIP file successfully created: {output_zip}")
            print(f"Log file created: {log_filename}")
        else:
            print(f"
Failed to create ZIP file. Check the log for details: {log_filename}")
            
    except KeyboardInterrupt:
        print("
Operation cancelled by user.")
    except Exception as e:
        print(f"
An error occurred: {e}")
        print(f"Check the log file for details: {log_filename}")
