###
# Created by: Curtis Szmania
# Date: 10/1/2015
# Initial Creation
###
# Modified by: Curtis Szmania
# Date: 5/21/2017
# Pep8 compliant.
###
from ast import literal_eval
from datetime import datetime
from configparser import ConfigParser
from logging import DEBUG, getLogger, FileHandler, Formatter, StreamHandler
from libs.lib import Lib
from libs.compress_images_lib import CompressImages_Lib
from libs.ffmpeg_lib import FFMPEG_Lib
from libs.mega_tools_lib import MegaTools_Lib
from os import path, remove, sep, walk
from path_mapping import PathMapping
from platform import system
from random import shuffle
from re import findall, IGNORECASE, match, search, sub
from string import Formatter as string_formatter
from syncprofile import SyncProfile
from sys import stdout
import sys
from threading import Thread
from time import sleep, time


reload(sys)
sys.setdefaultencoding('utf-8')

__author__ = 'szmania'

HOME_DIRECTORY = path.expanduser("~")


# MEGAMANAGER_CONFIG = 'megaManager.cfg'

# MEGA_ACCOUNTS_DATA = "megaAccounts_DATA.txt"
# MEGA_TOOLS_PATH = ''
# MEGA_ACCOUNTS = ''
# LOCAL_ROOT = ''
# REMOTE_ROOT = ''

# COMPRESSION_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png']
# COMPRESSION_VIDEO_EXTENSIONS = ['avi', 'flv', 'm4v', 'mkv', 'mp4', 'mpeg', 'mpg', 'wmv']
# IMAGE_TEMP_FILE_EXTENSIONS = ['compressimages-backup']

# COMPRESSION_FFMPEG_VIDEO_PRESET = 'medium'

# HOME_DIRECTORY = path.expanduser("~")
# TEMP_LOGFILE_PATH = gettempdir() + '{sep}megaManager_error_files_{randint}.tmp'.format(sep=sep,
#                                                                                        randint=randint(0, 9999999999))


# MEGA_MANAGER_CONFIG_DIR = HOME_DIRECTORY + "{sep}.mega_manager".format(sep=sep)
# MEGA_MANAGER_CONFIG_DIR_DATA = MEGA_MANAGER_CONFIG_DIR + '{sep}data'.format(sep=sep)
# MEGA_MANAGER_CONFIG_FILE_PATH = MEGA_MANAGER_CONFIG_DIR + "{sep}mega_manager.cfg".format(sep=sep)

# COMPRESSED_IMAGES_FILE = MEGA_MANAGER_CONFIG_DIR_DATA + "{sep}compressed_images.npy".format(sep=sep)
# UNABLE_TO_COMPRESS_IMAGES_FILE = MEGA_MANAGER_CONFIG_DIR_DATA + "{sep}unable_to_compress_images.npy".format(sep=sep)
# COMPRESSED_VIDEOS_FILE = MEGA_MANAGER_CONFIG_DIR_DATA + "{sep}compressed_videos.npy".format(sep=sep)
# UNABLE_TO_COMPRESS_VIDEOS_FILE = MEGA_MANAGER_CONFIG_DIR_DATA + "{sep}unable_to_compress_videos.npy".format(sep=sep)
# REMOVED_REMOTE_FILES = MEGA_MANAGER_CONFIG_DIR_DATA + '{sep}removed_remote_files.npy'.format(sep=sep)

# LOGFILE_STDOUT = MEGA_MANAGER_CONFIG_DIR + '{sep}logs{sep}mega_stdout.log'.format(sep=sep)
# LOGFILE_STDERR = MEGA_MANAGER_CONFIG_DIR + '{sep}logs{sep}mega_stderr.log'.format(sep=sep)
# MEGAMANAGER_LOGFILEPATH = MEGA_MANAGER_CONFIG_DIR + '{sep}logs{sep}mega_manager_log.log'.format(sep=sep)

# MEGA_TOOLS_DIR = 'tools\\megaTools_1_1_98'
# FFMPEG_EXE_PATH = 'tools{sep}ffmpeg{sep}ffmpeg.exe'.format(sep=sep)

# PROCESS_SET_PRIORITY_TIMEOUT = 60

# SCRIPT_DIR = path.dirname(path.realpath(__file__))
# SLEEP_TIME_BETWEEN_RUNS_SECONDS = 300  # 5 minutes
WORKING_DIR = path.dirname(path.realpath(__file__))


class MegaManager(object):
    def __init__(self, **kwargs):
        self.__threads = []
        self.__download = None
        self.__sync = None
        self.__upload = None
        self.__local_is_truth = None
        self.__remove_outdated = None
        self.__compress_all = None
        self.__compress_images = None
        self.__compress_videos = None
        self.__log_level = None

        self.__compressed_image_files = set()
        self.__compressed_video_files = set()
        self.__unable_to_compress_image_files = set()
        self.__unable_to_compress_video_files = set()
        self.__removed_remote_files = set()

        self.__sleep_time_between_runs_seconds = None

        self.__mega_manager_config_dir_path = None
        self.__mega_manager_config_dir_data_path = None
        self.__mega_manager_log_path = None
        self.__mega_manager_output_profile_data_path = None
        self.__compressed_images_file_path = None
        self.__compressed_videos_file_path = None
        self.__compression_image_extensions = []
        self.__compression_video_extensions = []
        self.__image_temp_file_extensions = []
        self.__compression_ffmpeg_video_preset = None
        # self.__megaManager_configPath = MEGAMANAGER_CONFIG
        self.__removed_remote_files_path = None
        self.__unable_to_compress_images_file_path = None
        self.__unable_to_compress_videos_file_path = None
        self.__process_set_priority_timeout = None
        self.__megatools_process_priority_class = None
        self.__megatools_log_path = None
        self.__mega_download_speed = None
        self.__mega_upload_speed = None
        self.__ffmpeg_process_priority_class = None
        self.__ffmpeg_log_path = None
        self.__ffmpeg_threads = None

        # self.__mega_tools_dir = MEGA_TOOLS_DIR
        # self.__ffmpeg_exe_path = FFMPEG_EXE_PATH

        self.__sync_profiles = []

        self._setup(kwargs=kwargs)

    def _assign_attributes(self, **kwargs):
        """
        Assign argumetns to class attributes.

        Args:
            kwargs (dict):  Dictionary of arguments.
        """

        for key, value in kwargs.items():
            if value:
                setattr(self, '_MegaManager__%s' % key, value)

    def _compress_image_file(self, file_path):
        """
        Compress given image file path.

        Args:
            file_path: Path to image file to compress.

        Returns:
            Boolean: Whether compression operation was successful or not.
        """
        logger = getLogger('MegaManager._compress_image_file')
        logger.setLevel(self.__log_level)
        logger.debug(' Compressing image file: "{}"'.format(file_path))
        compressed = self.__compress_images_lib.compress_image_file(file_path=file_path,
                                                                    jpeg_compression_quality_percentage=
                                                                    self.__compression_jpeg_quality_percentage,
                                                                    delete_backup=True,
                                                                    delete_corrupt_images=True)
        if compressed:
            logger.debug(' Image file compressed successfully "%s"!' % file_path)
            file_md5_hash = self.__lib.get_file_md5_hash(file_path)
            self.__compressed_image_files.add(file_md5_hash)
            self.__lib.dump_set_into_numpy_file(item_set=self.__compressed_image_files,
                                                file_path=self.__compressed_images_file_path)
            return True

        else:
            logger.debug(' Error, image file could not be compressed "%s"!' % file_path)
            file_md5_hash = self.__lib.get_file_md5_hash(file_path)
            self.__unable_to_compress_image_files.add(file_md5_hash)
            self.__lib.dump_set_into_numpy_file(item_set=self.__unable_to_compress_image_files,
                                                file_path=self.__unable_to_compress_images_file_path)
            return False

    def _compress_image_files(self, local_root):
        """
        Find image files to compress.

        Args:
            local_root (str): Local path to search for image files to compress

        Returns:
            Boolean: Returns whether operation was successful or not.
        """
        logger = getLogger('MegaManager._compress_image_files')
        logger.setLevel(self.__log_level)
        logger.debug(' Compressing image files.')

        try:
            if path.exists(local_root):
                local_files = [path.join(full_path, name) for full_path, subdirs, files in walk(local_root) for name in files]
                # local_files = [path.join(local_root, f) for f in listdir(local_root) if path.isfile(path.join(local_root, f))]
            else:
                raise PathMappingDoesNotExist(' Path mapping does not exist: {}'.format(local_root))

            if local_files:
                for local_file_path in local_files:
                    local_file_ext = local_file_path.split('.')[-1]
                    if local_file_ext in self.__image_temp_file_extensions or search('^.*\.megatmp\..*$', local_file_path):
                        logger.warning(' File "{}" is temporary file. Deleting.'.format(local_file_path))
                        self.__lib.delete_local_file(local_file_path)
                        continue

                    for compress_image_ext in self.__compression_image_extensions:
                        if match(local_file_ext, compress_image_ext, IGNORECASE) and path.isfile(local_file_path):
                            file_md5_hash = self.__lib.get_file_md5_hash(local_file_path)
                            if (file_md5_hash not in self.__compressed_image_files) \
                                    and (file_md5_hash not in self.__unable_to_compress_image_files):
                                self._compress_image_file(file_path=local_file_path)

            return True

        except Exception as e:
            logger.warning(' Exception: {}'.format(e))
            return False

    def _compress_video_file(self, file_path):
        """
        Compress given video file path.

        Args:
            file_path: Path to video file to compress.

        Returns:
            Boolean: Whether compression operation was successful or not.
        """
        logger = getLogger('MegaManager._compress_video_file')
        logger.setLevel(self.__log_level)

        logger.debug(' Compressing video file: "{}"'.format(file_path))
        temp_file_path = file_path.rsplit(".", 1)[0] + '_NEW.mp4'

        result = self.__ffmpeg_lib.compress_video_file(source_path=file_path, target_path=temp_file_path,
                                                       compression_preset=self.__compression_ffmpeg_video_preset,
                                                       ffmpeg_threads=self.__ffmpeg_threads, overwrite=True,
                                                       process_priority_class=self.__ffmpeg_process_priority_class,
                                                       process_set_priority_timeout=self.__process_set_priority_timeout)

        self._compress_video_file_teardown(result, file_path, temp_file_path)
        return result

    def _compress_video_file_setup(self, file_path, temp_file_path):
        """
        Setup for compress video file.

        Args:
            file_path (str): File path to compress.
            temp_file_path (str): Temporary file path.
        """
        logger = getLogger('MegaManager._compress_video_file_setup')
        logger.setLevel(self.__log_level)

        logger.debug(' Video file compression setup.')

        if path.exists(temp_file_path):
            self.__lib.delete_local_file(file_path=temp_file_path)

        for ext in self.__compression_video_extensions:
            possible_prev_file_path = file_path.rsplit(".", 1)[0] + ext
            if path.exists(possible_prev_file_path):
                self.__lib.delete_local_file(file_path=possible_prev_file_path)

    def _compress_video_file_teardown(self, result, file_path, temp_file_path):
        """
        Teardown for compress video file.

        Args:
            result (bool): Result of video file compression.
            file_path (str): File path to compress.
            temp_file_path (str): Temporary file path.
        """
        logger = getLogger('MegaManager._compress_video_file_teardown')
        logger.setLevel(self.__log_level)

        logger.debug(' Video file compression teardown.')

        if result and path.exists(temp_file_path):

            if path.exists(file_path):
                self.__lib.delete_local_file(file_path=file_path)

            new_file_path = sub('_NEW', '', temp_file_path)
            if path.exists(new_file_path):
                self.__lib.delete_local_file(file_path=new_file_path)

            if not self.__lib.rename_file(old_name=temp_file_path, new_name=new_file_path):
                self.__lib.delete_local_file(file_path=temp_file_path)

            logger.debug(' Video file compressed successfully "%s" into "%s"!' % (
                file_path, new_file_path))
            file_md5_hash = self.__lib.get_file_md5_hash(new_file_path)
            self.__compressed_video_files.add(file_md5_hash)
            self.__lib.dump_set_into_numpy_file(item_set=self.__compressed_video_files, file_path=self.__compressed_videos_file_path)

        elif path.exists(temp_file_path):
            logger.debug(' Error, video file could not be compressed "%s"!' % file_path)
            logger.debug(' Deleting temporary file "%s"!' % temp_file_path)
            self.__lib.delete_local_file(file_path=temp_file_path)

        else:
            logger.debug(' Error, video file could not be compressed "%s"!' % file_path)
            file_md5_hash = self.__lib.get_file_md5_hash(file_path)
            self.__unable_to_compress_video_files.add(file_md5_hash)
            self.__lib.dump_set_into_numpy_file(item_set=self.__unable_to_compress_video_files,
                                                file_path=self.__unable_to_compress_videos_file_path)

        logger.debug(' Successfully completed video file compression teardown.')

    def _compress_video_files(self, local_root):
        """
        Find video files to compress.

        Args:
            local_root (str): Local path to search for image files to compress

        Returns:
            Boolean: Whether operation is successful or not.
        """
        logger = getLogger('MegaManager._compress_video_files')
        logger.setLevel(self.__log_level)
        logger.debug(' Finding video files to compress in: "{}"'.format(local_root))

        try:
            if path.exists(local_root):
                local_files = [path.join(full_path, name) for full_path, subdirs, files in walk(local_root) for name in files]
                if local_files:
                    for local_file_path in local_files:
                        if local_file_path.endswith('_NEW.mp4') or search('^.*\.megatmp\..*$', local_file_path):
                            logger.warning(' File "{}" is a temporary file. Deleting.'.format(local_file_path))
                            self.__lib.delete_local_file(local_file_path)
                            continue

                        local_file_ext = local_file_path.split('.')[-1]
                        # local_file_ext = path.splitext(local_file_path)[1]
                        for compress_video_ext in self.__compression_video_extensions:
                            if match(local_file_ext, compress_video_ext, IGNORECASE):
                                file_md5_hash = self.__lib.get_file_md5_hash(local_file_path)
                                if (file_md5_hash not in self.__compressed_video_files) \
                                    and (file_md5_hash not in self.__unable_to_compress_video_files):

                                    self._compress_video_file(file_path=local_file_path)
                else:
                    logger.warning(' No files found in path: "{}"'.format(local_root))

                logger.debug(' Success, finished finding video files to compress in: "{}"'.format(local_root))
                return True
            else:
                raise PathMappingDoesNotExist(' Path mapping does not exist: "{}"'.format(local_root))

        except Exception as e:
            logger.warning(' Exception: {}'.format(e))
            return False

    def _create_thread_get_profile_data(self, profile):
        """
        Create thread to create profiles data file.

        Args:
            profile (Profile): Profile object

        Returns:
            Boolean: Whether operation was successful or not.
        """

        logger = getLogger('MegaManager._create_thread_get_profile_data')
        logger.setLevel(self.__log_level)

        # logger.debug(' Creating thread to create "%s" file.' % self.__mega_accounts_output_path)

        try:
            t = Thread(target=self._get_profile_data, args=(profile,),
                       name='thread_get_profile_data_{}'.format(profile.profile_name))
            self.__threads.append(t)
            t.start()
            return True
        except Exception as e:
            logger.warning('Exception: {}'.format(e))
            return False

    def _create_thread_download(self, profile):
        """
        Create thread to download files.

        Args:
            profile (Profile): Profile object

        Returns:
            Boolean: Whether operation was successful or not.
        """

        logger = getLogger('MegaManager._create_thread_download')
        logger.setLevel(self.__log_level)

        try:
            logger.debug(' Creating thread to download files from MEGA account profile {}.'.format(profile.profile_name))

            t = Thread(target=self._thread_download_profile_files, args=(profile,),
                       name='thread_download_{}'.format(profile.profile_name))
            self.__threads.append(t)
            t.start()
            return True
        except Exception as e:
            logger.warning(' Exception: {}'.format(e))
            return False

    def _create_thread_upload(self, profile):
        """
        Create thread to upload files.

        Args:
            profile (Profile): Profile object

        Returns:
            Boolean: Whether operation was successful or not.
        """

        logger = getLogger('MegaManager._create_thread_upload')
        logger.setLevel(self.__log_level)

        logger.debug(' Creating thread to upload files to MEGA accounts.')

        try:
            t = Thread(target=self._thread_upload_profile_files, args=(profile, ),
                       name='thread_upload_{}'.format(profile.profile_name))
            self.__threads.append(t)
            t.start()
            return True
        except Exception as e:
            logger.warning(' Exception: {}'.format(e))
            return False

    def _create_thread_remove_remote_files_that_dont_exist_locally(self, profile):
        """
        Create threads to remove remote files that don't exist locally.

        Args:
            profile (Profile): Profile object

        Retruns:
            Boolean: Whether successful or not.
        """
        logger = getLogger('MegaManager._create_thread_remove_remote_files_that_dont_exist_locally')
        logger.setLevel(self.__log_level)
        try:
            logger.debug(' Creating thread to remove remote files that dont exist locally for profile {}.'.format(
                profile.profile_name))
            t_remove_remote_files_dont_exist_locally = Thread(target=self._thread_remove_remote_files_that_dont_exist_locally,
                                                              args=(profile,),
                                             name='thread_remove_remote_files_dont_exist_locally_{}'.format(
                                                 profile.profile_name))
            self.__threads.append(t_remove_remote_files_dont_exist_locally)
            t_remove_remote_files_dont_exist_locally.start()
            return True

        except Exception as e:
            logger.error(' Exception: {}'.format(e))
            return False

    def _create_thread_compress_image_files(self, sync_profiles):
        """
        Create thread to compress image files.

        Args:
            sync_profiles (SyncProfile): SyncProfiles objects

        Retruns:
            Boolean: Whether successful or not.
        """

        logger = getLogger('MegaManager._create_thread_compress_image_files')
        logger.setLevel(self.__log_level)

        logger.debug(' Creating thread to compress local image files')

        try:
            t_compress = Thread(target=self._thread_sync_profiles_image_compression, args=(sync_profiles,), name='thread_compress_images')
            self.__threads.append(t_compress)
            t_compress.start()
            return True
        except Exception as e:
            logger.error(' Exception: {}'.format(e))
            return False

    def _create_thread_compress_video_files(self, sync_profiles):
        """
        Create thread to compress video files.

        Args:
            sync_profiles (SyncProfile): SyncProfile objects

        Retruns:
            Boolean: Whether successful or not.
        """

        logger = getLogger('MegaManager._create_thread_compress_video_files')
        logger.setLevel(self.__log_level)

        logger.debug(' Creating thread to compress local video files.')

        try:
            t_compress = Thread(target=self._thread_sync_profiles_video_compression, args=(sync_profiles,), name='thread_compress_videos')
            self.__threads.append(t_compress)
            t_compress.start()
            return True
        except Exception as e:
            logger.error(' Exception: {}'.format(e))
            return False

    def _create_thread_output_profile_data(self, profile):
        """
        Create thread to output profile data

        Args:
            profile (Profile): Profile object

        Retruns:
            Boolean: Whether successful or not.
        """

        logger = getLogger('MegaManager._create_thread_output_profile_data')
        logger.setLevel(self.__log_level)

        logger.debug(' Creating thread to output profile data for {}'.format(profile.profile_name))

        try:
            t_output = Thread(target=self._thread_output_profile_data, args=(profile,), name='thread_output_profile_data_{}'.format(profile.profile_name))
            self.__threads.append(t_output)
            t_output.start()
            return True
        except Exception as e:
            logger.error(' Exception: {}'.format(e))
            return False

    def _export_accounts_details_dict(self):
        """
        Dump self.__accounts_details_dict to file.

        """

        logger = getLogger('MegaManager._export_accounts_details_dict')
        logger.setLevel(self.__log_level)
        logger.debug(' Exporting config data to MEGA Manager config file.')

        # with open(self.__mega_accounts_output_path, "w") as outs:
        #     for username in sorted(self.__accounts_details_dict):
        #         accountObj = self.__accounts_details_dict[username]
        #         lines = []
        #         line = 'Total Space: ' + str(accountObj.remote_total_space)
        #         lines.append(line)
        #         line = 'Used Space: ' + str(accountObj.remote_used_space)
        #         lines.append(line)
        #         line = 'Free Space: ' + str(accountObj.remote_free_space)
        #         lines.append(line)
        #         outs.write(lines)
        # outs.close()

    def _export_config_file_data(self, config_parser):
        """
        Export config file data.

        Args:
            config_parser (ConfigParser): Config parser object of config file.

        """

        logger = getLogger('MegaManager._export_config_file_data')
        logger.setLevel(self.__log_level)

        logger.debug(' Exporting config data to MEGA Manager config file.')
        try:
            with open(self.__mega_manager_config_path, 'w') as config_file:
                config_parser.write(config_file)
            # with open(self.__mega_manager_config_path, "w") as outs:
            #     outs.write('MEGA_TOOLS_DIR=%s' % str(self.__mega_tools_dir))
            #     outs.write('FFMPEG_EXE_PATH=%s' % str(self.__ffmpeg_exe_path))
            #     outs.write('SLEEP_TIME_BETWEEN_RUNS_SECONDS=%s' % str(self.__sleep_time_between_runs_seconds))
            #
            #     profileCount = 0
            #     for profile in self.__sync_profiles:
            #         profileCount += 1
            #         outs.write('[Profile%d]' % profileCount)
            #         outs.write('ProfileName=%s' % str(profile.profile_name))
            #         outs.write('Username=%s' % str(profile.account.username))
            #         outs.write('Password=%s' % str(profile.account.password))
            #
            #         pathMappingsCount = 0
            #         for pathMapping in profile.path_mappings:
            #             pathMappingsCount += 1
            #             outs.write('LocalPath%d=%s' % (pathMappingsCount, str(pathMapping.local_path)))
            #             outs.write('RemotePath%d=%s' % (pathMappingsCount, str(pathMapping.remotPath)))
            #
            # outs.close()
            return True
        except Exception as e:
            logger.error(' Exception: %s' % str(e))
            return False


    def _get_accounts_user_pass(self, file):
        """
        Get username and password from file with lines of "<username> - <password>"

        Args:
            file (str): file in format with lines:

                "<username> - <password>"
                "<username2> - <password2>"

            Where <username> is account username and <password> is account password.

        Returns:
            Returns list of dictionaries holding user and pass.
        """

        logger = getLogger('MegaManager._get_accounts_user_pass')
        logger.setLevel(self.__log_level)

        logger.debug(' Getting usernames and passwords.')

        foundUserPass = []

        try:
            with open(file, "r") as ins:
                for line in ins:
                    dict = {}
                    if len(findall('-', line)) > 0 and len(findall('@', line)) > 0:
                        username = sub('\\n', '', sub(' - .*', '', line))
                        password = sub('\\n', '', sub('.* - ', '', line))

                        dict['user'] = username
                        dict['pass'] = password
                        foundUserPass.append(dict)
            ins.close()
        except Exception as e:
            logger.warning(' Exception: %s' % str(e))

        return foundUserPass

    def _get_profile_data(self, profile):
        """
        Create self.__mega_accounts_output_path file. File that has all fetched data of accounts and local and remote spaces of each account.

        Args:
            profile (Profile): Profile object

        Retruns:
            Boolean: Whether successful or not.
        """

        logger = getLogger('MegaManager._get_profile_data')
        logger.setLevel(self.__log_level)

        # logger.debug(' Creating MEGA accounts output file.')

        try:
            # self.__accounts_details_dict = {}
            # with open(self.__mega_accounts_output_path, "w") as outs:
            # for profile in self.__sync_profiles:
            logger.debug(' Creating thread to gather details for profile "%s".' % profile.profile_name)

            self._get_profile_details(profile=profile)
            # t_megaFile = Thread(target=self._get_profile_details, args=(profile, ),
            #                     name='thread_get_profile_data_%s' % profile.profile_name)
            # t_megaFile.start()
            # self.__threads.append(t_megaFile)

            # outs.close()
            return True
        except (Exception, KeyboardInterrupt)as e:
            logger.warning(' Exception: {}'.format(e))
            # if path.exists(self.__mega_accounts_output_path + '.old'):
            #     copyfile(self.__mega_accounts_output_path + '.old', self.__mega_accounts_output_path)
            return False

    def _get_profile_details(self, profile):
        """
        Creats dictionary of account data (remote size, local size, etc...) for self.__mega_accounts_output_path file.

        Args:
            profile (SyncProfile): Profile to get data for.
        """

        self._update_account_remote_details(account=profile.account)

    def _get_remote_file_modified_date(self, username, password, localFilePath, localRoot, remoteRoot):
        """
        Get remote file modified date of equivalent local file path

        Args:
            username (str): username for MEGA account
            password (str): password for MEGA account
            localFilePath (str): Local file path of remote file size to get
            localRoot (str): Local root path of local account files to map with remote root.
            remoteRoot (str): Remote root path of remote accounts to map with local root.

        Returns:
             Tuple: Remote file modified data and remote file path
        """

        logger = getLogger('MegaManager.-get_remote_file_modified_date')
        logger.setLevel(self.__log_level)

        remotePath = self.__lib.get_remote_path_from_local_path(localPath=localFilePath, localRoot=localRoot,
                                                                remoteRoot=remoteRoot)
        if remotePath:
            return self.__mega_tools_lib.get_remote_file_modified_date(username=username, password=password,
                                                                       remotePath=remotePath)
        logger.warning(' Remote file path could not be gotten.')
        return None

    def _get_remote_files_that_dont_exist_locally(self, username, password, local_root, remote_root):
        """
        Get remote files that don't exist locally.

        Args:
            username (str): username of account to upload to
            password (str): Password of account to upload to
            local_root (str): Local path to download file to
            remote_root (str): Remote path of file to download

        Returns:
            list of remote files that don't exist locally
        """

        logger = getLogger('MegaManager._get_remote_files_that_dont_exist_locally')
        logger.setLevel(self.__log_level)

        logger.debug(' Getting remote files that do not exist locally on %s - %s.' % (username, password))

        remote_files = self.__mega_tools_lib.get_remote_file_paths_recursively(username=username, password=password,
                                                                               remote_path=remote_root,
                                                                               process_priority_class=self.__megatools_process_priority_class,
                                                                               process_set_priority_timeout=self.__process_set_priority_timeout)
        dont_exist_locally = []
        try:
            if remote_files:
                for remote_file_path in remote_files:
                    file_sub_path = sub(remote_root, '', remote_file_path)
                    local_file_path = local_root + file_sub_path.replace('/', '{sep}'.format(sep=sep))

                    if not path.exists(local_file_path):
                        found = False
                        for not_exist_local_file_path in dont_exist_locally:
                            if local_file_path in not_exist_local_file_path:
                                found = True
                                break
                        if not found:
                            dont_exist_locally.append(remote_file_path)

        except Exception as e:
            logger.warning(' Exception: {}'.format(e))
        finally:
            return dont_exist_locally

    def _import_config_file_data(self, ignore_config_actions):
        """
        Load config file data.

        Args:
            ignore_config_actions (bool): Whether to ignore config file OPTIONS section

        Returns:
            ConfigParser: Config parser object.
        """
        print(' Loading MEGA Manager config file.')

        config_parser = ConfigParser()
        try:
            print(' Loading config file: {}'.format(self.__mega_manager_config_path))
            if path.exists(self.__mega_manager_config_path):
                config_parser.read(self.__mega_manager_config_path)
            else:
                raise Exception('Config file not found!')
        except Exception as e:
            print(' Exception: {}'.format(e))
            raise e

        self._import_config_file_properties(config_parser=config_parser, ignore_config_actions=ignore_config_actions)
        self._import_config_mega_profile_data(config_parser=config_parser)
        print(' Successfully imported sections from config file: {}'.format(config_parser.sections()))
        return config_parser


    def _import_config_mega_profile_data(self, config_parser):
        """
        Load config profile data.

        Args:
            config_parser (object): ConfigParser object.
        """
        print(' Loading MEGA profile data.')
        try:
            sync_profile_obj = None
            for section in config_parser:
                profile_name = None
                username = None
                password = None
                sync_profiles = []
                if section.startswith('PROFILE_'):
                    profile_name = config_parser[section]['profile_name']
                    username = config_parser[section]['username']
                    password = config_parser[section]['password']
                    path_mappings = []

                    for entry in config_parser[section]:
                        local_path = None
                        remote_path = None
                        path_mapping_entry = None
                        if entry.startswith('local_path_'):
                            local_path = config_parser[section][entry]
                            remote_path = config_parser[section][entry.replace('local_path_','remote_path_')]
                            path_mapping_entry = PathMapping(local_path=local_path, remote_path=remote_path, log_level=self.__log_level)
                            path_mappings.append(path_mapping_entry)
                    sync_profile_obj = SyncProfile(profile_name=profile_name, username=username, password=password,
                                                   path_mappings=path_mappings)
                    self.__sync_profiles.append(sync_profile_obj)
        except Exception as e:
            print(' Exception: {}'.format(e))
            raise e

        print(' Successfully loaded MEGA profile data from config.')
        return sync_profile_obj

    def _import_config_file_properties(self, config_parser, ignore_config_actions):
        """
        Import config file data properties sections.

        Args:
            config_parser (ConfigParser): Config parser object.
            ignore_config_actions (bool): Whether to ignore config file OPTIONS section

        """
        print(' Loading MEGA Manager config file properties data.')
        config_key_values = {}
        for section in config_parser.sections():
            if not section.startswith('PROFILE_') and (not ignore_config_actions or (ignore_config_actions and not section == 'ACTIONS')):
                for key, value in (config_parser[section].items()):
                    try:
                        placeholders_in_str = {}
                        format_placeholders = [fn for _, fn, _, _ in string_formatter().parse(value) if fn is not None]
                        found = False
                        for format_placeholder in format_placeholders:
                            if format_placeholder.lower() in config_key_values:
                                found = True
                                placeholders_in_str[format_placeholder] = config_key_values[format_placeholder.lower()].replace('"','')
                        if 'sep' in format_placeholders:
                            found = True
                            placeholders_in_str['sep'] = sep
                        if 'HOME_DIRECTORY' in format_placeholders:
                            found = True
                            placeholders_in_str['HOME_DIRECTORY'] = HOME_DIRECTORY.replace('"','')
                        if found:
                            value = value.format(**placeholders_in_str)
                        setattr(self, '_MegaManager__{}'.format(key.lower()), literal_eval(value))
                        config_key_values[key] = value
                    except Exception as e:
                        print(' Exception: {}'.format(e))
                        raise e

        print(' Successfully loaded MEGA Manager config file properties data.')

    def _remove_outdated_files(self, username, password, local_root, remote_root):
        """
        Remove old versions of files.

        Args:
            username (str): username for MEGA account
            password (str): password for MEGA account
            local_root (str): Local path to download file to
            remote_root (str): Remote path of file to download

        Returns:
            Boolean: Whether operation was successful or not.
        """
        logger = getLogger('MegaManager.remove_outdated_files')
        logger.setLevel(self.__log_level)
        logger.debug(' Removing outdated files for username "{}"'.format(username))

        try:
            lines = self.__mega_tools_lib.get_remote_file_data_recursively(username=username, password=password,
                                                                           remote_path=remote_root, remove_blank_lines=True)
            if lines:
                for line in lines:
                    logger.debug(' Processing line "%s"' % line)
                    remote_file_type = self.__mega_tools_lib.get_file_type_from_megals_line_data(line=line)

                    if remote_file_type == '0':
                        remote_file_path = self.__mega_tools_lib.get_file_path_from_megals_line_data(line=line)
                        remote_file_size = self.__mega_tools_lib.get_file_size_from_megals_line_data(line=line)
                        remote_file_modified_date = self.__mega_tools_lib.get_file_date_from_megals_line_data(line=line)
                        remote_file_modified_date_dt = datetime.strptime(remote_file_modified_date, '%Y-%m-%d %H:%M:%S')
                        remote_root = remote_root.replace('/', '{sep}'.format(sep=sep))
                        local_root = local_root
                        conv_remote_file_path = remote_file_path.replace('/', '{sep}'.format(sep=sep))
                        local_file_path = conv_remote_file_path.replace(remote_root, local_root)

                        if path.exists(local_file_path):
                            logger.debug(' Local file exists. Determining if local file outdated compared to remote counterpart: "%s"' % local_file_path)
                            local_file_size = path.getsize(local_file_path)

                            if search('^.*\.megatmp\..*$', local_file_path):
                                logger.warning(' File "{}" is temporary file. Deleting.'.format(local_file_path))
                                self.__lib.delete_local_file(local_file_path)
                                continue

                            local_file_modified_date = self.__lib.convert_epoch_to_mega_time(path.getmtime(local_file_path))
                            local_file_modified_date_dt = datetime.strptime(local_file_modified_date, '%Y-%m-%d %H:%M:%S')

                            if local_file_size != int(remote_file_size):
                                if local_file_modified_date_dt > remote_file_modified_date_dt:
                                    # local file is newer.
                                    logger.debug(' Local file is newer. Deleting remote file "%s"' % remote_file_path)

                                    self.__mega_tools_lib.remove_remote_path(username=username, password=password,
                                                                             remote_file_path=remote_file_path,
                                                                             process_priority_class=self.__megatools_process_priority_class,
                                                                             process_set_priority_timeout=self.__process_set_priority_timeout)
                                    logger.debug(' Success, removed local incomplete file "{}"'.format(local_file_path))

                                else:
                                    # remote file is newer
                                    logger.debug(' Remote file is newer. Deleting local file "%s"' % local_file_path)

                                    for retry in range(100):
                                        try:
                                            remove(local_file_path)
                                            logger.debug(' Success, removed local incomplete file "{}"'.format(local_file_path))
                                            break
                                        except Exception as e:
                                            logger.exception(' Remove failed for remote file, "{}" retrying...'.format(e))
                        else:
                            logger.debug(' Local file does NOT exist: "%s"' % local_file_path)
                    else:
                        logger.debug(' Remote location is not a file: "{}"'.format(line))
            else:
                logger.debug(' No file list retrieved from MEGA for account "{}"'.format(username))

            logger.debug(' Finished removing outdated files for username "{}"'.format(username))
            return True
        except Exception as e:
            logger.warning(' Exception: {}'.format(e))
            return False

    def _remove_outdated_local_remote_files(self, profile):
        """
        Remove outdated local and remote files

        Args:
            profile (Profile): Profile object
        """
        logger = getLogger('MegaManager._remove_outdated_local_remote_files')
        logger.setLevel(self.__log_level)

        try:
            profile_name = profile.profile_name
            logger.debug(' Removing outdated files for {}'.format(profile_name))
            username = profile.account.username
            password = profile.account.password

            for pathMapping in profile.path_mappings:
                local_path = pathMapping.local_path
                remote_path = pathMapping.remote_path
                self._remove_outdated_files(username=username, password=password, local_root=local_path,
                                            remote_root=remote_path)
        except Exception as e:
            logger.error('Exception: {}'.format(e))

    def _remove_remote_files_that_dont_exist_locally(self, username, password, local_root, remote_root):
        """
        Remove remote files that don't exist locally.

        Args:
            username (str): username of account to upload to
            password (str): Password of account to upload to
            local_root (str): Local path to download file to
            remote_root (str): Remote path of file to download

        Returns:
            Boolean: Whether operation is successful or not.
        """
        logger = getLogger('MegaManager._remove_remote_files_that_dont_exist_locally')
        logger.setLevel(self.__log_level)
        logger.debug(' Removing remote files that do not exist locally for account: "{}"'.format(username))
        dont_exist_locally = self._get_remote_files_that_dont_exist_locally(username=username, password=password,
                                                                            local_root=local_root, remote_root=remote_root)
        try:
            for file_path in dont_exist_locally:
                file_md5_hash = self.__lib.get_file_md5_hash(file_path)
                self.__removed_remote_files.add(file_md5_hash)
                self.__mega_tools_lib.remove_remote_path(username=username, password=password,
                                                         remote_file_path=file_path,
                                                         process_priority_class=self.__megatools_process_priority_class,
                                                         process_set_priority_timeout=self.__process_set_priority_timeout)
                self.__lib.dump_set_into_numpy_file(item_set=self.__removed_remote_files,
                                                    file_path=self.__removed_remote_files_path)
            return True

        except Exception as e:
            logger.error('Exception: {}'.format(e))
            return False

    def _remove_temp_files(self):
        """
        Remove MEGA Manager temporary files.

        Returns:
            Bool: Whether successful or not.
        """
        logger = getLogger('MegaManager._remove_temp_files')
        logger.setLevel(self.__log_level)

        logger.info(' Removing temporary files!')
        try:
            # dir = self.__mega_manager_config_dir_data_path
            # files = listdir(dir)
            #
            # for file in files:
            #     if file.endswith('.npy'):
            #         file_path = dir + '{sep}'.format(sep=sep) + file
            #         self.__lib.delete_local_file(file_path=file_path)
            return True

        except Exception as e:
            logger.error(' Exception: {}'.format(e))
            return False

    def _setup(self, kwargs):
        """
        Setup MegaManager applicaiton.

        Args:
            kwargs (dict): Mega_Manager keyword arguments.
        """

        try:
            self.__mega_manager_config_path = kwargs['mega_manager_config_path']
            ignore_config_actions = False
            for key, value in kwargs.items():
                if value == True:
                    ignore_config_actions = True
            self.__config_parser = self._import_config_file_data(ignore_config_actions=ignore_config_actions)
            self._assign_attributes(**kwargs)
            self.__lib = Lib(log_level=self.__log_level)
            self._setup_logger(log_file_path=self.__mega_manager_log_path)

            self.__compress_images_lib = CompressImages_Lib(log_level=self.__log_level)
            self.__ffmpeg_lib = FFMPEG_Lib(log_file_path=self.__ffmpeg_log_path, log_level=self.__log_level)
            self.__mega_tools_lib = MegaTools_Lib(log_file_path=self.__megatools_log_path, down_speed_limit=self.__mega_download_speed, up_speed_limit=self.__mega_upload_speed, log_level=self.__log_level)

            self.__removed_remote_files = self.__lib.load_numpy_file_as_set(file_path=self.__removed_remote_files_path)
            self.__compressed_video_files = self.__lib.load_numpy_file_as_set(file_path=self.__compressed_videos_file_path)
            self.__unable_to_compress_video_files = self.__lib.load_numpy_file_as_set(
                file_path=self.__unable_to_compress_videos_file_path)
            self.__compressed_image_files = self.__lib.load_numpy_file_as_set(file_path=self.__compressed_images_file_path)
            self.__unable_to_compress_image_files = self.__lib.load_numpy_file_as_set(
                file_path=self.__unable_to_compress_images_file_path)

        except Exception as e:
            print(' Exception: ' + str(e))
            self._teardown()

    def _setup_logger(self, log_file_path):
        """
        Logger setup.

        Args:
            log_file_path (str):  Log file path.
        """
        print(' Setting up logger using log file: {}'.format(log_file_path))
        if path.exists(log_file_path):
            try:
                remove(log_file_path)
            except Exception as e:
                print(' Exception: %s' % str(e))
                pass

        root = getLogger()
        root.setLevel(DEBUG)

        self.__handler = FileHandler(log_file_path)
        formatter = Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
        # formatter = logging.Formatter(fmt='%(message)s', datefmt='')
        self.__handler.setLevel(DEBUG)
        self.__handler.setFormatter(formatter)

        ch = StreamHandler(stdout)
        ch.setLevel(self.__log_level)
        ch.setFormatter(formatter)

        root.addHandler(self.__handler)
        root.addHandler(ch)

        logger = getLogger('MegaManager._setup_logger')
        logger.setLevel(self.__log_level)
        logger.info(' Logging to %s' % self.__mega_manager_log_path)

    def _teardown(self):
        """
        Tearing down of MEGA Manager.
        """

        logger = getLogger('MegaManager._teardown')
        logger.setLevel(self.__log_level)

        logger.info(' Tearing down megaManager!')
        try:
            if self.__sync:
                self.__lib.dump_set_into_numpy_file(item_set=self.__removed_remote_files,
                                                    file_path=self.__removed_remote_files_path, )
            if self.__compress_images:
                self.__lib.dump_set_into_numpy_file(item_set=self.__compressed_image_files,
                                                    file_path=self.__compressed_images_file_path, )
                self.__lib.dump_set_into_numpy_file(item_set=self.__unable_to_compress_image_files,
                                                    file_path=self.__unable_to_compress_images_file_path)
            if self.__compress_videos:
                self.__lib.dump_set_into_numpy_file(item_set=self.__compressed_video_files,
                                                    file_path=self.__compressed_videos_file_path, )
                self.__lib.dump_set_into_numpy_file(item_set=self.__unable_to_compress_video_files,
                                                    file_path=self.__unable_to_compress_videos_file_path)

            self._remove_temp_files()

            megacopy_process_name = 'megacopy.exe' if system() == 'Windows' else 'megacopy'
            self.__lib.kill_running_processes_with_name(megacopy_process_name)
            megals_process_name = 'megals.exe' if system() == 'Windows' else 'megals'
            self.__lib.kill_running_processes_with_name(megals_process_name)
            megadf_process_name = 'megadf.exe' if system() == 'Windows' else 'megadf'
            self.__lib.kill_running_processes_with_name(megadf_process_name)
            megarm_process_name = 'megarm.exe' if system() == 'Windows' else 'megarm'
            self.__lib.kill_running_processes_with_name(megarm_process_name)
            megamkdir_process_name = 'megamkdir.exe' if system() == 'Windows' else 'megamkdir'
            self.__lib.kill_running_processes_with_name(megamkdir_process_name)
            ffmpeg_process_name = 'ffmpeg.exe' if system() == 'Windows' else 'ffmpeg'
            self.__lib.kill_running_processes_with_name(ffmpeg_process_name)

            logger.info(' Tear down successful!')
        except Exception as e:
            logger.warning(' Exception: %s' % str(e))
            pass

    def _thread_download_profile_files(self, profile):
        """
        Download files from profile.

        Args:
            profile (Profile): Profile object

        Returns:
            Boolean: Whether operation was successful or not.
        """

        logger = getLogger('MegaManager._thread_download_profile_files')
        logger.setLevel(self.__log_level)

        for pathMapping in profile.path_mappings:
            self.__mega_tools_lib.download_all_files_from_account(username=profile.account.username,
                                                                password=profile.account.password,
                                                                local_root=pathMapping.local_path,
                                                                remote_root=pathMapping.remote_path,
                                                                process_set_priority_timeout=self.__process_set_priority_timeout)

            # self.__mega_tools_lib.download_all_files_from_account(account['user'], account['pass'], self.__local_root, self.__remote_root)


    def _thread_output_profile_data(self, profile):
        """
        Output profile data to standard output.

        Args:
            profile (Profile): Profile object

        Retruns:
            Boolean: Whether successful or not.
        """

        logger = getLogger('MegaManager._thead_output_profile_data')
        logger.setLevel(self.__log_level)

        try:
            print('')
            print('')
            print('Profile Data Output:')
            print(('\tProfile Name: {}').format(profile.profile_name))
            print(('\tLocal Used Space: {}').format(profile.local_used_space))
            print(('\tRemote Free Space: {}').format(profile.remote_free_space))
            print(('\tRemote Total Space: {}').format(profile.remote_total_space))
            print(('\tRemote Used Space: {}').format(profile.remote_used_space))
            print(('\tAccount Username: {}').format(profile.account.username))
            print(('\tAccount Password: {}').format(profile.account.password))
            print('')

        except Exception as e:
            logger.warning('Exception: {}'.format(e))

    def _thread_remove_remote_files_that_dont_exist_locally(self, profile):
        """
        Get remote files that don't exist locally.

        Args:
            profile (SyncProfile): Profile to remove remote files that dont exist locally.

        Returns:
            Boolean: whether operation is successful or not
        """

        logger = getLogger('MegaManager._thread_remove_remote_files_that_dont_exist_locally')
        logger.setLevel(self.__log_level)
        logger.debug(' Removing files that do not exist locally for profile: "{}"'.format(profile.profile_name))
        for path_mapping in profile.path_mappings:
            local_root = path_mapping.local_path
            remote_root = path_mapping.remote_path
            username = profile.account.username
            password = profile.account.password
            self._remove_outdated_files(username=username, password=password, local_root=local_root, remote_root=remote_root)
            self._remove_remote_files_that_dont_exist_locally(username=username, password=password, local_root=local_root,
                                                              remote_root=remote_root)

    def _thread_sync_profiles_image_compression(self, sync_profiles):
        """
        Compress image.

        Args:
            sync_profiles (SyncProfile): syncProfile objects

        Retruns:
            Boolean: Whether successful or not.
        """

        logger = getLogger('MegaManager._thread_sync_profiles_image_compression')
        logger.setLevel(self.__log_level)

        logger.debug(' Compressing local image files')

        try:
            for profile in sync_profiles:
                for path_mapping in profile.path_mappings:
                    logger.debug(' Compressing image files for profile: "{}"'.format(profile.profile_name))
                    self._compress_image_files(local_root=path_mapping.local_path)
            return True
        except Exception as e:
            logger.warning(' Exception: {}'.format(e))
            return False

    def _thread_sync_profiles_video_compression(self, syncProfiles):
        """
        Compress video.

        Args:
            syncProfiles (SyncProfile): syncProfile objects

        Retruns:
            Boolean: Whether successful or not.
        """

        logger = getLogger('MegaManager._thread_syncprofiles_video_compression')
        logger.setLevel(self.__log_level)
        logger.debug(' Compressing local video files')
        try:
            for profile in syncProfiles:
                for pathMapping in profile.path_mappings:
                    self._compress_video_files(local_root=pathMapping.local_path)
            return True
        except Exception as e:
            logger.warning(' Exception: {}'.format(e))
            return False

    def _thread_upload_profile_files(self, profile):
        """
        Upload to all MEGA profile accounts.

        Args:
            profile (Profile): Profile object

        Retruns:
            Boolean: Whether successful or not.
        """

        logger = getLogger('MegaManager._thead_download_profile_files')
        logger.setLevel(self.__log_level)

        try:
            for pathMapping in profile.path_mappings:
                self.__mega_tools_lib.upload_to_account(username=profile.account.username, password=profile.account.password,
                                                        local_root=pathMapping.local_path,
                                                        remote_root=pathMapping.remote_path,
                                                        process_priority_class=self.__megatools_process_priority_class,
                                                        process_set_priority_timeout=self.__process_set_priority_timeout)
        except Exception as e:
            logger.warning(' Exception: {}'.format(e))

    def _update_account_remote_details(self, account):
        """
        Gather data for account (remote used space, remote free space, remote total space, etc...).

        Args:
            account (Account): Account object to gather data for.

        Returns:
            Account: account object with remote data updated
        """

        logger = getLogger('MegaManager._update_account_remote_details')
        logger.setLevel(self.__log_level)

        username = account.username
        password = account.password

        account.total_space = self.__mega_tools_lib.get_account_total_space(username=username, password=password)

        account.free_space = self.__mega_tools_lib.get_account_free_space(username=username, password=password)

        account.used_space = self.__mega_tools_lib.get_account_used_space(username=username, password=password)

        # accountDetails.append('REMOTE SIZE: ' + used_space)
        #
        # subDirs = self.__mega_tools_lib.get_remote_subdir_names_only(username=username, password=password, remote_path=self.__remote_root)
        #
        # directoryLines = []
        # totalLocalSize = 0
        #
        # if subDirs:
        #     for line in subDirs:
        #         localDirSize = 0
        #         localDirPath = self.__local_root + '\\' + line
        #
        #         if path.exists(localDirPath) and not line == '':
        #             for r, d, f in walk(localDirPath):
        #                 for file in f:
        #                     filePath = path.join(r, file)
        #                     if path.exists(filePath):
        #                         localDirSize = localDirSize + path.getsize(filePath)
        #
        #             totalLocalSize = totalLocalSize + localDirSize
        #             remoteDirSize = self.__mega_tools_lib.get_remote_dir_size(username, password, localDirPath,
        #                                                                  localRoot=self.__local_root,
        #                                                                  remoteRoot=self.__remote_root)
        #
        #             directoryLines.append(line +
        #                                   ' (%s remote, %s local)\n' % (self.__lib.get_mb_size_from_bytes(int(remoteDirSize)), self.__lib.get_mb_size_from_bytes(int(localDirSize))))
        #
        #         elif not line == '':
        #             directoryLines.append(line + ' (%s remote, NONE local)\n' % (self.__lib.get_mb_size_from_bytes(int(remoteDirSize))))
        #
        #     accountDetails.append('LOCAL SIZE: %s \n' % self.__lib.get_mb_size_from_bytes(totalLocalSize))
        #
        #     for line in directoryLines:
        #         accountDetails.append(line)
        #     accountDetails.append('\n')
        #     accountDetails.append('\n')
        #
        #     self.__accounts_details_dict[username] = accountDetails

        return account

    def _update_profile_remote_details(self, profile):
        """
        Gather data for profile (remote size, local size, etc...) for self.__mega_accounts_output_path file.

        Args:
            profile (SyncProfile): profile object to gather data for.

        Returns:
            SyncProfile: profile object with remote data updated
        """

        logger = getLogger('MegaManager._update_profile_remote_details')
        logger.setLevel(self.__log_level)

        username = profile.account.username
        password = profile.account.password
        totalRemoteSize = 0

        for pathMapping in profile.path_mappings:
            remotePath = pathMapping.remotepath
            remotePaths = self.__mega_tools_lib.get_remote_file_paths_recursively(username=username, password=password,
                                                                                  remote_path=remotePath,
                                                                                  process_priority_class=self.__megatools_process_priority_class,
                                                                                  process_set_priority_timeout=self.__process_set_priority_timeout)

            pathMappingRemoteSize = 0
            for path in remotePaths:
                pathMappingRemoteSize += self.__mega_tools_lib.get_remote_file_size(username=username, password=password, remotePath=path)

            pathMapping.remote_path_used_space = pathMappingRemoteSize
            totalRemoteSize += pathMappingRemoteSize
        return profile

    def _wait_for_threads_to_finish(self, threads=None, timeout=9999999):
        """
        Wait for threads to finish.

        Args:
            timeout (int): Maximum time in seconds to wait for threads.
        """
        logger = getLogger('MegaManager._wait_for_threads_to_finish')
        logger.setLevel(self.__log_level)

        threads = threads if threads else self.__threads
        logger.debug(' Waiting for threads to finish: {}'.format(threads))
        start_time = time()

        while len(threads) > 0:
            if not time() - start_time > timeout:
                for thread in threads:
                    if not thread.isAlive():
                        threads.remove(thread)
                        logger.info(' Thread "%s" finished!' % thread.name)
                        logger.debug(' Threads left: %d' % len(threads))
            else:
                logger.debug(' Waiting for threads to complete TIMED OUT! Timeout %d (seconds)' % timeout)
                return

    def get_mega_manager_log_file(self):
        """
        Returns Mega Manager logging file path.

        Returns:
             Mega Manager logging file path.
        """
        
        return self.__mega_manager_log_path

    def run(self):
        """
        Run MegaManager tasks.

        Returns:
            Integer: Returns 0 for successful or 1 for unsuccessful.
        """

        logger = getLogger('MegaManager.run')
        logger.setLevel(self.__log_level)

        logger.debug(' Running MEGA Manager.')

        result = 0
        try:
            while True:
                sync_profiles_randomized = self.__sync_profiles[:]
                shuffle(sync_profiles_randomized)
                if self.__compress_all:
                    self._create_thread_compress_image_files(sync_profiles=sync_profiles_randomized)
                    self._create_thread_compress_video_files(sync_profiles=sync_profiles_randomized)
                elif self.__compress_images:
                    self._create_thread_compress_image_files(sync_profiles=sync_profiles_randomized)
                elif self.__compress_videos:
                    self._create_thread_compress_video_files(sync_profiles=sync_profiles_randomized)

                non_profile_threads = list(self.__threads)
                for profile in sync_profiles_randomized:

                    if self.__mega_manager_output_profile_data_path:
                        self._create_thread_output_profile_data(profile=profile)

                    # if self.__remove_outdated:
                    #     self._remove_outdated_local_remote_files(profile=profile)

                    if self.__sync:
                        if self.__local_is_truth:
                            self._thread_remove_remote_files_that_dont_exist_locally(profile=profile)
                        else:
                            self._create_thread_remove_remote_files_that_dont_exist_locally(profile=profile)
                        # self._thread_download_profile_files(profile=profile)
                        self._create_thread_download(profile=profile)
                        # self._thread_upload_profile_files(profile=profile)
                        self._create_thread_upload(profile=profile)
                        # self._remove_outdated_local_remote_files(profile=profile)

                    # if self.__download:
                    #     # self._thread_download_profile_files(profile=profile)
                    #     self._create_thread_download(profile=profile)
                    # if self.__upload:
                    #     # self._thread_upload_profile_files(profile=profile)
                    #     self._create_thread_upload(profile=profile)
                    # if self.__remove_remote:
                    #     self._create_thread_remove_remote_files_that_dont_exist_locally(profile=profile)

                    profile_threads = [item for item in self.__threads if item not in non_profile_threads]
                    self._wait_for_threads_to_finish(threads=profile_threads)

                self._wait_for_threads_to_finish()
                logger.debug(' Sleeping {} seconds before next run.'.format(self.__sleep_time_between_runs_seconds))
                sleep(self.__sleep_time_between_runs_seconds)

        except Exception as e:
            logger.debug(' Exception: ' + str(e))
            result = 1
        finally:
            self._teardown()
            return result


class PathMappingDoesNotExist(Exception):
    pass

def main():
    pass


if __name__ == "__main__":
    main()


