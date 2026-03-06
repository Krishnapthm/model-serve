# ROCm vLLM Container Troubleshooting

Status: **open** — container exits immediately with `RuntimeError: Failed to infer device type`.

---

## Symptom

Every vLLM container spawned by the backend exits with exit code 1 within seconds.
Backend marks the served model as `error`.

Container logs:

```
RuntimeError: Failed to infer device type, please set the environment variable
`VLLM_LOGGING_LEVEL=DEBUG` to turn on verbose logging to help debug the issue.
```

The crash originates in `vllm/config/device.py::DeviceConfig.__post_init__` which
calls `current_platform.device_type`. When that returns an empty string vLLM aborts.
This happens **during argument parser initialization** — before any `--device` flag is
parsed — so passing `--device rocm` does not help.

---

## Investigation log

### Fix 1 — enumerate `/dev/dri` device files individually

**Root cause identified:** The Docker Python SDK's `devices` list requires *file*
paths. Passing `"/dev/dri"` (a directory) silently skips `renderD128` / `card0`,
so the container starts with no DRI devices mounted.

**Fix applied** (`vllm_manager.py`):

```python
def _rocm_devices() -> list[str]:
    devices = ["/dev/kfd"]
    for pattern in ("/dev/dri/renderD*", "/dev/dri/card*"):
        devices.extend(sorted(glob.glob(pattern)))
    return devices
```

This produces `['/dev/kfd', '/dev/dri/renderD128', '/dev/dri/card0']` on the
current host.

**Result: did not fix it.** Even with correct device file paths and `group_add:
["video", "render"]`, PyTorch reports `torch.cuda.is_available() == False`.

### Fix 2 — add `render` group (GID 991)

Docker group names inside the container resolve to the container's `/etc/group`,
where `render` is GID 109. The host `render` group is GID **991**. Passing the
group name `"render"` adds GID 109 — wrong. The `/dev/kfd` and `/dev/dri/renderD128`
devices on the host are owned by GID 991.

**Attempted:** pass numeric GIDs `44` (video) and `991` (render).

**Result: did not fix it.** `torch.cuda.is_available()` still returns `False` even
with numeric host GIDs.

### Fix 3 — `--privileged`

**Attempted:**

```bash
docker run --rm --privileged --ipc host \
  --entrypoint bash vllm/vllm-openai-rocm:latest \
  -c "python3 -c 'import torch; print(torch.cuda.is_available())'"
```

**Result: `False`.** GPU is not visible even in a fully privileged container.

---

## Current hypothesis

The AMD GPU hardware is present (`amdgpu` kernel module loaded, `/dev/kfd` exists)
but the ROCm userspace stack on the **host** is not fully initialized:

- `rocminfo` is not installed (`apt install rocminfo` needed to verify)
- `torch.cuda.is_available()` returns `False` even outside Docker
- The `/sys/class/kfd/kfd/topology/` node names were not checked

This points to a **host-side ROCm stack issue**, not a Docker flag issue. The
container flags (`--device`, `group_add`, `ipc_mode`, `seccomp`) are now correct
and match the official vLLM ROCm docs.

---

## Next steps to try

1. **Verify host ROCm stack:**

   ```bash
   apt install rocminfo
   rocminfo           # should list GPU nodes
   python3 -c "import torch; print(torch.version.hip, torch.cuda.device_count())"
   ```

2. **Check KFD topology:**

   ```bash
   ls /sys/class/kfd/kfd/topology/nodes/
   cat /sys/class/kfd/kfd/topology/nodes/1/name
   ```

3. **Check ROCm driver version compatibility:**
   The host `amdgpu` kernel driver version must be compatible with the ROCm
   userspace in `vllm/vllm-openai-rocm:latest`. Run:

   ```bash
   cat /sys/module/amdgpu/version 2>/dev/null || modinfo amdgpu | grep ^version
   docker run --rm --entrypoint bash vllm/vllm-openai-rocm:latest \
     -c "cat /opt/rocm/.info/version"
   ```

4. **Try `rocm/vllm-dev:nightly`** (AMD's image, different from the upstream
   vLLM image — entrypoint is `/bin/bash`):

   ```bash
   docker run -it --rm \
     --network host --group-add video --ipc host \
     --cap-add SYS_PTRACE --security-opt seccomp=unconfined \
     --device /dev/kfd --device /dev/dri \
     rocm/vllm-dev:nightly \
     python3 -c "import torch; print(torch.cuda.is_available())"
   ```

5. **Check if `ROCR_VISIBLE_DEVICES` needs to be set:**

   ```bash
   docker run --rm ... -e ROCR_VISIBLE_DEVICES=0 vllm/vllm-openai-rocm:latest ...
   ```

---

## Related files

- [`backend/app/services/vllm_manager.py`](../backend/app/services/vllm_manager.py) — container spawn logic
- [`docker/compose.rocm.yml`](../docker/compose.rocm.yml) — ROCm compose stack
- [vLLM ROCm Docker docs](https://docs.vllm.ai/en/stable/deployment/docker/#amd-rocm)
