use std::path::PathBuf;
use std::process::{Child, Command};
use std::sync::Mutex;
use tauri::Manager;

fn get_python_path() -> PathBuf {
    // Try project venv first
    let venv_python = PathBuf::from("/Users/lianwenhua/indie/Agents/copaw/projects/cineMate/.venv/bin/python3");
    if venv_python.exists() {
        return venv_python;
    }
    // Fallback to system python3
    PathBuf::from("python3")
}

pub struct AppState {
    python_process: Mutex<Option<Child>>,
}

#[tauri::command]
fn get_service_status(state: tauri::State<AppState>) -> Result<String, String> {
    let mut proc = state.python_process.lock().map_err(|e| e.to_string())?;
    match *proc {
        Some(ref mut child) => match child.try_wait() {
            Ok(None) => Ok("running".into()),
            Ok(Some(_)) => Ok("exited".into()),
            Err(e) => Err(e.to_string()),
        },
        None => Ok("not_started".into()),
    }
}

#[tauri::command]
fn restart_python_service(state: tauri::State<AppState>) -> Result<String, String> {
    let mut proc = state.python_process.lock().map_err(|e| e.to_string())?;
    if let Some(mut child) = proc.take() {
        let _ = child.kill();
    }
    let child = Command::new(get_python_path())
        .args(["-m", "cine_mate.api.server", "--port", "8787"])
        .spawn()
        .map_err(|e| format!("Failed to start Python service: {}", e))?;
    *proc = Some(child);
    Ok("started".into())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_log::Builder::new().build())
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_fs::init())
        .manage(AppState {
            python_process: Mutex::new(None),
        })
        .invoke_handler(tauri::generate_handler![
            get_service_status,
            restart_python_service
        ])
        .setup(|app| {
            let handle = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                std::thread::sleep(std::time::Duration::from_secs(1));
                let state = handle.state::<AppState>();
                let mut proc = state.python_process.lock().unwrap();
                if proc.is_none() {
                    match Command::new(get_python_path())
                        .args(["-m", "cine_mate.api.server", "--port", "8787"])
                        .spawn()
                    {
                        Ok(child) => {
                            *proc = Some(child);
                            log::info!("Python service started on port 8787");
                        }
                        Err(e) => {
                            log::error!("Failed to auto-start Python service: {}", e);
                        }
                    }
                }
            });
            Ok(())
        })
        .on_window_event(|app, event| {
            if let tauri::WindowEvent::Destroyed = event {
                if let Ok(mut proc) = app.state::<AppState>().python_process.lock() {
                    if let Some(mut child) = proc.take() {
                        let _ = child.kill();
                        log::info!("Python service stopped");
                    }
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
