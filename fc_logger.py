import logging

LOG_FILE_PATH = "fermentation_controller.log"


def init_fc_logger():
    logging.basicConfig(filename="fermentation_controller.log",
                        filemode='w',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.DEBUG)
    return logging.getLogger("FC_Logger")


FC_LOGGER = logging.getLogger('FC_Logger')
