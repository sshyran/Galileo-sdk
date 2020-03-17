from typing import Any, Callable, Optional, List
from urllib.parse import urlunparse

import requests
from ..providers.auth import AuthProvider
from .settings import SettingsRepository
from galileo_sdk.business.objects import Job, JobStatus, EJobStatus
from datetime import datetime


class JobsRepository:
    def __init__(
        self, settings_repository: SettingsRepository, auth_provider: AuthProvider,
    ):
        self._settings_repository = settings_repository
        self._auth_provider = auth_provider

    def _make_url(
        self,
        endpoint: str,
        params: Optional[str] = "",
        query: Optional[str] = "",
        fragment: Optional[str] = "",
    ):
        settings = self._settings_repository.get_settings()
        backend = settings.backend
        schema, addr = backend.split("://")
        return urlunparse(
            (
                schema,
                f"{addr}/galileo/user_interface/v1",
                endpoint,
                params,
                query,
                fragment,
            )
        )

    def _request(
        self,
        request: Callable,
        endpoint: str,
        data: Optional[Any] = None,
        params: Optional[str] = None,
        query: Optional[str] = None,
        fragment: Optional[str] = None,
    ):
        url = self._make_url(endpoint, params, query, fragment)
        access_token = self._auth_provider.get_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
        r = request(url, json=data, headers=headers)
        r.raise_for_status()
        return r

    def _get(self, *args, **kwargs):
        return self._request(requests.get, *args, **kwargs)

    def _post(self, *args, **kwargs):
        return self._request(requests.post, *args, **kwargs)

    def _put(self, *args, **kwargs):
        return self._request(requests.put, *args, **kwargs)

    def _delete(self, *args, **kwargs):
        return self._request(requests.delete, *args, **kwargs)

    def request_send_job(self):
        return self._get("/job/upload_request")

    def request_send_job_completed(
        self, destination_mid: str, file_name: str, station_id: str
    ):
        return self._post(
            "/jobs",
            {
                "destination_mid": destination_mid,
                "filename": file_name,
                "stationid": station_id,
            },
        )

    def request_receive_job(self, job_id: str):
        return self._get(f"/jobs/{job_id}/results/location")

    def request_receive_job_completed(self, job_id: str):
        return self._put(f"/jobs/{job_id}/results/download_complete")

    def submit_job(self, job_id: str):
        return self._put(f"/jobs/{job_id}/run")

    def request_stop_job(self, job_id: str):
        return self._put(f"/jobs/{job_id}/stop")

    def request_pause_job(self, job_id: str):
        return self._put(f"/jobs/{job_id}/pause")

    def request_start_job(self, job_id: str):
        return self._put(f"/jobs/{job_id}/start")

    def request_top_from_job(self, job_id: str):
        return self._get(f"/jobs/{job_id}/top")

    def request_logs_from_jobs(self, job_id: str):
        return self._get(f"/jobs/{job_id}/logs")

    def list_jobs(self, query: str) -> List[Job]:
        response = self._get("/jobs", query=query)
        json: dict = response.json()
        jobs: List[dict] = json["jobs"]
        return [job_dict_to_job(job) for job in jobs]

    def get_results_url(self, job_id: str):
        return self._get(f"/jobs/{job_id}/results")

    def download_results(self, job_id: str, query: str):
        return self._get(f"/jobs/{job_id}/results", query=query)


def job_dict_to_job(job: dict) -> Job:
    return Job(
        job["jobid"],
        job["receiverid"],
        job["project_id"],
        datetime.fromtimestamp(job["time_created"]),
        datetime.fromtimestamp(job["last_updated"]),
        job["status"],
        job["container"],
        job["name"],
        job["stationid"],
        job["userid"],
        job["state"],
        job["oaid"],
        job["pay_status"],
        job["pay_interval"],
        job["total_runtime"],
        job["archived"],
        [
            job_status_dict_to_job_status(job_status)
            for job_status in job["status_history"]
        ],
    )


def job_status_dict_to_job_status(job_status: dict) -> JobStatus:
    status = JobStatus(
        datetime.fromtimestamp(job_status["time"]), EJobStatus[job_status["status"]],
    )
    status.jobstatusid = (
        job_status["jobstatusid"] if "jobstatusid" in job_status else None
    )
    status.jobid = job_status["jobid"] if "jobid" in job_status else None
