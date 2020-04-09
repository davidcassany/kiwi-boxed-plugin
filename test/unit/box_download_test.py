import io
from mock import (
    patch, Mock, MagicMock, call
)

from kiwi_boxed_plugin.box_download import BoxDownload


class TestBoxDownload:
    @patch('kiwi_boxed_plugin.defaults.Defaults.get_box_config_file')
    @patch('kiwi_boxed_plugin.box_download.Path')
    def setup(self, mock_Path, mock_get_box_config_file):
        mock_get_box_config_file.return_value = '../data/boxes.yml'
        self.box = BoxDownload('suse')
        mock_Path.create.assert_called_once_with(
            '/var/cache/kiwi/boxes/suse'
        )
        self.result = self.box.vm_setup_type(
            system='/var/cache/kiwi/boxes/suse/'
            'SUSE-Box.x86_64-1.42.1-System-BuildBox.qcow2',
            kernel='/var/cache/kiwi/boxes/suse/kernel',
            initrd=None
        )

    @patch('kiwi_boxed_plugin.box_download.Command.run')
    @patch('kiwi_boxed_plugin.box_download.Uri')
    @patch('kiwi_boxed_plugin.box_download.SolverRepository')
    @patch('kiwi_boxed_plugin.box_download.Checksum')
    @patch('os.path.exists')
    def test_fetch_checksum_did_not_match(
        self, mock_os_path_exist, mock_Checksum, mock_SolverRepository,
        mock_Uri, mock_Command_run
    ):
        checksum = Mock()
        checksum.matches.return_value = False
        checksum.sha256.return_value = 'sum'
        mock_Checksum.return_value = checksum
        repo = Mock()
        mock_SolverRepository.return_value = repo
        mock_os_path_exist.return_value = False
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value = MagicMock(spec=io.IOBase)
            file_handle = mock_open.return_value.__enter__.return_value
            assert self.box.fetch(update_check=True) == self.result
            mock_open.assert_called_once_with(
                '/var/cache/kiwi/boxes/suse/'
                'SUSE-Box.x86_64-1.42.1-System-BuildBox.packages.sha256', 'w'
            )
            file_handle.write.assert_called_once_with('sum')
            assert repo.download_from_repository.call_args_list == [
                call(
                    'SUSE-Box.x86_64-1.42.1-System-BuildBox.packages',
                    '/var/cache/kiwi/boxes/suse/'
                    'SUSE-Box.x86_64-1.42.1-System-BuildBox.packages'
                ),
                call(
                    'SUSE-Box.x86_64-1.42.1-Kernel-BuildBox.tar.xz',
                    '/var/cache/kiwi/boxes/suse/'
                    'SUSE-Box.x86_64-1.42.1-Kernel-BuildBox.tar.xz'
                ),
                call(
                    'SUSE-Box.x86_64-1.42.1-System-BuildBox.qcow2',
                    '/var/cache/kiwi/boxes/suse/'
                    'SUSE-Box.x86_64-1.42.1-System-BuildBox.qcow2'
                )
            ]
            mock_Command_run.assert_called_once_with(
                [
                    'tar', '-C', '/var/cache/kiwi/boxes/suse',
                    '--transform', 's/.*/kernel/',
                    '--wildcards', '-xf',
                    '/var/cache/kiwi/boxes/suse/'
                    'SUSE-Box.x86_64-1.42.1-Kernel-BuildBox.tar.xz',
                    '*.kernel'
                ]
            )

    @patch('kiwi_boxed_plugin.box_download.Command.run')
    @patch('kiwi_boxed_plugin.box_download.Uri')
    @patch('kiwi_boxed_plugin.box_download.SolverRepository')
    @patch('kiwi_boxed_plugin.box_download.Checksum')
    @patch('os.path.exists')
    def test_fetch_checksum_matches(
        self, mock_os_path_exist, mock_Checksum, mock_SolverRepository,
        mock_Uri, mock_Command_run
    ):
        checksum = Mock()
        checksum.matches.return_value = True
        checksum.sha256.return_value = 'sum'
        mock_Checksum.return_value = checksum
        repo = Mock()
        mock_SolverRepository.return_value = repo
        mock_os_path_exist.return_value = True
        assert self.box.fetch(update_check=True) == self.result
        repo.download_from_repository.assert_called_once_with(
            'SUSE-Box.x86_64-1.42.1-System-BuildBox.packages',
            '/var/cache/kiwi/boxes/suse/'
            'SUSE-Box.x86_64-1.42.1-System-BuildBox.packages'
        )
        mock_Command_run.assert_called_once_with(
            [
                'tar', '-C', '/var/cache/kiwi/boxes/suse',
                '--transform', 's/.*/kernel/',
                '--wildcards', '-xf',
                '/var/cache/kiwi/boxes/suse/'
                'SUSE-Box.x86_64-1.42.1-Kernel-BuildBox.tar.xz',
                '*.kernel'
            ]
        )

    @patch('kiwi_boxed_plugin.box_download.Command.run')
    @patch('kiwi_boxed_plugin.box_download.Uri')
    @patch('kiwi_boxed_plugin.box_download.SolverRepository')
    @patch('kiwi_boxed_plugin.box_download.Checksum')
    @patch('os.path.exists')
    def test_fetch_update_check_disabled(
        self, mock_os_path_exist, mock_Checksum, mock_SolverRepository,
        mock_Uri, mock_Command_run
    ):
        mock_os_path_exist.return_value = True
        assert self.box.fetch(update_check=False) == self.result
        mock_Command_run.assert_called_once_with(
            [
                'tar', '-C', '/var/cache/kiwi/boxes/suse',
                '--transform', 's/.*/kernel/',
                '--wildcards', '-xf',
                '/var/cache/kiwi/boxes/suse/'
                'SUSE-Box.x86_64-1.42.1-Kernel-BuildBox.tar.xz',
                '*.kernel'
            ]
        )