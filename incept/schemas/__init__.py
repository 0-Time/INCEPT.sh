"""Schema registry mapping IntentLabel to param model classes."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from incept.schemas.intents import IntentLabel
from incept.schemas.ir import AnyIR, ClarificationIR, ConfidenceScore, PipelineIR, SingleIR
from incept.schemas.params.archive_ops import CompressArchiveParams, ExtractArchiveParams
from incept.schemas.params.disk_ops import MountDeviceParams, UnmountDeviceParams
from incept.schemas.params.file_ops import (
    ChangeOwnershipParams,
    ChangePermissionsParams,
    CompareFilesParams,
    CopyFilesParams,
    CreateDirectoryParams,
    CreateSymlinkParams,
    DeleteFilesParams,
    DiskUsageParams,
    FindFilesParams,
    ListDirectoryParams,
    MoveFilesParams,
    ViewFileParams,
)
from incept.schemas.params.log_ops import FilterLogsParams, FollowLogsParams, ViewLogsParams
from incept.schemas.params.networking import (
    DownloadFileParams,
    NetworkInfoParams,
    PortCheckParams,
    SshConnectParams,
    TestConnectivityParams,
    TransferFileParams,
)
from incept.schemas.params.package_mgmt import (
    InstallPackageParams,
    RemovePackageParams,
    SearchPackageParams,
    UpdatePackagesParams,
)
from incept.schemas.params.process_mgmt import (
    KillProcessParams,
    ProcessListParams,
    SystemInfoParams,
)
from incept.schemas.params.scheduling import ListCronParams, RemoveCronParams, ScheduleCronParams
from incept.schemas.params.service_mgmt import (
    EnableServiceParams,
    RestartServiceParams,
    ServiceStatusParams,
    StartServiceParams,
    StopServiceParams,
)
from incept.schemas.params.special import ClarifyParams, OutOfScopeParams, UnsafeRequestParams
from incept.schemas.params.text_processing import (
    CountLinesParams,
    ExtractColumnsParams,
    ReplaceTextParams,
    SearchTextParams,
    SortOutputParams,
    UniqueLinesParams,
)
from incept.schemas.params.user_mgmt import CreateUserParams, DeleteUserParams, ModifyUserParams

INTENT_PARAM_REGISTRY: dict[IntentLabel, type[BaseModel]] = {
    # File Operations (12)
    IntentLabel.find_files: FindFilesParams,
    IntentLabel.copy_files: CopyFilesParams,
    IntentLabel.move_files: MoveFilesParams,
    IntentLabel.delete_files: DeleteFilesParams,
    IntentLabel.change_permissions: ChangePermissionsParams,
    IntentLabel.change_ownership: ChangeOwnershipParams,
    IntentLabel.create_directory: CreateDirectoryParams,
    IntentLabel.list_directory: ListDirectoryParams,
    IntentLabel.disk_usage: DiskUsageParams,
    IntentLabel.view_file: ViewFileParams,
    IntentLabel.create_symlink: CreateSymlinkParams,
    IntentLabel.compare_files: CompareFilesParams,
    # Text Processing (6)
    IntentLabel.search_text: SearchTextParams,
    IntentLabel.replace_text: ReplaceTextParams,
    IntentLabel.sort_output: SortOutputParams,
    IntentLabel.count_lines: CountLinesParams,
    IntentLabel.extract_columns: ExtractColumnsParams,
    IntentLabel.unique_lines: UniqueLinesParams,
    # Archive Operations (2)
    IntentLabel.compress_archive: CompressArchiveParams,
    IntentLabel.extract_archive: ExtractArchiveParams,
    # Package Management (4)
    IntentLabel.install_package: InstallPackageParams,
    IntentLabel.remove_package: RemovePackageParams,
    IntentLabel.update_packages: UpdatePackagesParams,
    IntentLabel.search_package: SearchPackageParams,
    # Service Management (5)
    IntentLabel.start_service: StartServiceParams,
    IntentLabel.stop_service: StopServiceParams,
    IntentLabel.restart_service: RestartServiceParams,
    IntentLabel.enable_service: EnableServiceParams,
    IntentLabel.service_status: ServiceStatusParams,
    # User Management (3)
    IntentLabel.create_user: CreateUserParams,
    IntentLabel.delete_user: DeleteUserParams,
    IntentLabel.modify_user: ModifyUserParams,
    # Log Operations (3)
    IntentLabel.view_logs: ViewLogsParams,
    IntentLabel.follow_logs: FollowLogsParams,
    IntentLabel.filter_logs: FilterLogsParams,
    # Scheduling (3)
    IntentLabel.schedule_cron: ScheduleCronParams,
    IntentLabel.list_cron: ListCronParams,
    IntentLabel.remove_cron: RemoveCronParams,
    # Networking (6)
    IntentLabel.network_info: NetworkInfoParams,
    IntentLabel.test_connectivity: TestConnectivityParams,
    IntentLabel.download_file: DownloadFileParams,
    IntentLabel.transfer_file: TransferFileParams,
    IntentLabel.ssh_connect: SshConnectParams,
    IntentLabel.port_check: PortCheckParams,
    # Process Management (3)
    IntentLabel.process_list: ProcessListParams,
    IntentLabel.kill_process: KillProcessParams,
    IntentLabel.system_info: SystemInfoParams,
    # Disk/Mount (2)
    IntentLabel.mount_device: MountDeviceParams,
    IntentLabel.unmount_device: UnmountDeviceParams,
    # Special (3)
    IntentLabel.CLARIFY: ClarifyParams,
    IntentLabel.OUT_OF_SCOPE: OutOfScopeParams,
    IntentLabel.UNSAFE_REQUEST: UnsafeRequestParams,
}


def get_param_model(intent: IntentLabel) -> type[BaseModel]:
    """Get the param model class for a given intent."""
    return INTENT_PARAM_REGISTRY[intent]


def validate_params(intent: IntentLabel, params: dict[str, Any]) -> BaseModel:
    """Validate params dict against the schema for an intent. Returns validated model."""
    model_cls = get_param_model(intent)
    return model_cls(**params)


__all__ = [
    "AnyIR",
    "ClarificationIR",
    "ConfidenceScore",
    "INTENT_PARAM_REGISTRY",
    "IntentLabel",
    "PipelineIR",
    "SingleIR",
    "get_param_model",
    "validate_params",
]
