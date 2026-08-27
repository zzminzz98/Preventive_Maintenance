import logging

def setup_logger(name=__name__):
    # Configure standard logger
    logging.basicConfig(
        level=logging.INFO,
            format = "%(asctime)s - %(levelname)s - %(message)s"        
    )
    return logging.getLogger(name)
    
