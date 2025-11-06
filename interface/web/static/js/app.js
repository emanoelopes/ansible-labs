// Ansible Labs Web Interface JavaScript

const API_BASE = window.location.origin;
let currentExecutionId = null;
let pollInterval = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadData();
    setupEventListeners();
});

// Load data from API
async function loadData() {
    try {
        // Check API health first
        try {
            const healthResponse = await fetch(`${API_BASE}/api/health`);
            if (!healthResponse.ok) {
                throw new Error('API health check failed');
            }
        } catch (healthError) {
            console.error('API health check failed:', healthError);
            showError('API não está respondendo. Certifique-se de que o servidor está rodando (python run_web.py)');
            return;
        }

        // Load groups
        try {
            const groupsResponse = await fetch(`${API_BASE}/api/inventory/groups`);
            if (!groupsResponse.ok) {
                throw new Error(`Failed to load groups: ${groupsResponse.status} ${groupsResponse.statusText}`);
            }
            const groups = await groupsResponse.json();
            renderGroups(groups);
        } catch (error) {
            console.error('Error loading groups:', error);
            showError(`Erro ao carregar grupos: ${error.message}`);
        }

        // Load hosts
        try {
            const hostsResponse = await fetch(`${API_BASE}/api/inventory/hosts`);
            if (!hostsResponse.ok) {
                throw new Error(`Failed to load hosts: ${hostsResponse.status} ${hostsResponse.statusText}`);
            }
            const hosts = await hostsResponse.json();
            renderHosts(hosts);
        } catch (error) {
            console.error('Error loading hosts:', error);
            showError(`Erro ao carregar hosts: ${error.message}`);
        }

        // Load playbooks
        try {
            const playbooksResponse = await fetch(`${API_BASE}/api/playbooks`);
            if (!playbooksResponse.ok) {
                throw new Error(`Failed to load playbooks: ${playbooksResponse.status} ${playbooksResponse.statusText}`);
            }
            const playbooks = await playbooksResponse.json();
            renderPlaybooks(playbooks);
        } catch (error) {
            console.error('Error loading playbooks:', error);
            showError(`Erro ao carregar playbooks: ${error.message}`);
        }

        // Load tags
        try {
            const tagsResponse = await fetch(`${API_BASE}/api/tags`);
            if (!tagsResponse.ok) {
                throw new Error(`Failed to load tags: ${tagsResponse.status} ${tagsResponse.statusText}`);
            }
            const tags = await tagsResponse.json();
            renderTags(tags);
        } catch (error) {
            console.error('Error loading tags:', error);
            showError(`Erro ao carregar tags: ${error.message}`);
        }

        updateExecuteButton();
    } catch (error) {
        console.error('Error loading data:', error);
        showError(`Erro ao carregar dados: ${error.message}`);
    }
}

// Show error message
function showError(message) {
    // Create or update error display
    let errorDiv = document.getElementById('error-message');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.id = 'error-message';
        errorDiv.style.cssText = 'position: fixed; top: 20px; right: 20px; background: #dc3545; color: white; padding: 15px 20px; border-radius: 5px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); z-index: 10000; max-width: 400px;';
        document.body.appendChild(errorDiv);
    }
    errorDiv.innerHTML = `<strong>Erro:</strong><br>${message}<br><br><button onclick="this.parentElement.remove()" style="background: white; color: #dc3545; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer;">Fechar</button>`;
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
        if (errorDiv && errorDiv.parentElement) {
            errorDiv.remove();
        }
    }, 10000);
}

// Render groups
function renderGroups(groups) {
    const container = document.getElementById('groups-container');
    container.innerHTML = '';
    
    groups.forEach(group => {
        const div = document.createElement('div');
        div.className = 'checkbox-item';
        div.innerHTML = `
            <input type="checkbox" id="group-${group.name}" value="${group.name}" data-type="group">
            <label for="group-${group.name}">${group.name} (${group.hosts.length} hosts)</label>
        `;
        container.appendChild(div);
    });
}

// Render hosts
function renderHosts(hosts) {
    const container = document.getElementById('hosts-container');
    container.innerHTML = '';
    
    hosts.forEach(host => {
        const div = document.createElement('div');
        div.className = 'checkbox-item';
        const ip = host.ip || host.ansible_host || '';
        div.innerHTML = `
            <input type="checkbox" id="host-${host.name}" value="${host.name}" data-type="host">
            <label for="host-${host.name}">${host.name}${ip ? ` (${ip})` : ''}</label>
        `;
        container.appendChild(div);
    });
}

// Render playbooks
function renderPlaybooks(playbooks) {
    const select = document.getElementById('playbook-select');
    select.innerHTML = '<option value="">Selecione um playbook...</option>';
    
    playbooks.forEach(pb => {
        const option = document.createElement('option');
        option.value = pb.name;
        option.textContent = pb.name + (pb.description ? ` - ${pb.description}` : '');
        select.appendChild(option);
    });
}

// Render tags
function renderTags(tags) {
    const container = document.getElementById('tags-container');
    container.innerHTML = '';
    
    const sortedTags = tags.sort();
    sortedTags.forEach(tag => {
        const div = document.createElement('div');
        div.className = 'checkbox-item';
        div.innerHTML = `
            <input type="checkbox" id="tag-${tag}" value="${tag}" data-type="tag">
            <label for="tag-${tag}">${tag}</label>
        `;
        container.appendChild(div);
    });
}

// Setup event listeners
function setupEventListeners() {
    // Checkbox changes
    document.addEventListener('change', (e) => {
        if (e.target.type === 'checkbox') {
            updateSelectedCount();
            updateSelectedTags();
            updateExecuteButton();
        }
    });

    // Playbook selection
    document.getElementById('playbook-select').addEventListener('change', () => {
        updateExecuteButton();
    });

    // Execute button
    document.getElementById('execute-btn').addEventListener('click', executePlaybook);
    
    // Cancel button
    document.getElementById('cancel-btn').addEventListener('click', cancelExecution);
}

// Update selected count
function updateSelectedCount() {
    const selected = document.querySelectorAll('input[type="checkbox"]:checked');
    const count = Array.from(selected).filter(cb => 
        cb.dataset.type === 'group' || cb.dataset.type === 'host'
    ).length;
    document.getElementById('selected-count').textContent = count;
}

// Update selected tags
function updateSelectedTags() {
    const selected = Array.from(document.querySelectorAll('input[type="checkbox"]:checked'))
        .filter(cb => cb.dataset.type === 'tag')
        .map(cb => cb.value);
    
    const display = selected.length > 0 ? selected.join(', ') : 'nenhuma';
    document.getElementById('selected-tags').textContent = display;
}

// Update execute button state
function updateExecuteButton() {
    const playbook = document.getElementById('playbook-select').value;
    const selected = document.querySelectorAll('input[type="checkbox"]:checked');
    const hasSelection = Array.from(selected).some(cb => 
        cb.dataset.type === 'group' || cb.dataset.type === 'host'
    );
    
    const btn = document.getElementById('execute-btn');
    btn.disabled = !playbook || !hasSelection;
}

// Execute playbook
async function executePlaybook() {
    const playbook = document.getElementById('playbook-select').value;
    const selectedGroups = Array.from(document.querySelectorAll('input[type="checkbox"]:checked'))
        .filter(cb => cb.dataset.type === 'group')
        .map(cb => cb.value);
    const selectedHosts = Array.from(document.querySelectorAll('input[type="checkbox"]:checked'))
        .filter(cb => cb.dataset.type === 'host')
        .map(cb => cb.value);
    const selectedTags = Array.from(document.querySelectorAll('input[type="checkbox"]:checked'))
        .filter(cb => cb.dataset.type === 'tag')
        .map(cb => cb.value);

    // Build hosts list (include hosts from selected groups)
    let hosts = [...selectedHosts];
    
    // Get hosts from selected groups
    if (selectedGroups.length > 0) {
        try {
            const groupsResponse = await fetch(`${API_BASE}/api/inventory/groups`);
            const groups = await groupsResponse.json();
            
            selectedGroups.forEach(groupName => {
                const group = groups.find(g => g.name === groupName);
                if (group) {
                    group.hosts.forEach(host => {
                        if (!hosts.includes(host.name)) {
                            hosts.push(host.name);
                        }
                    });
                }
            });
        } catch (error) {
            console.error('Error getting group hosts:', error);
        }
    }

    const requestBody = {
        playbook: playbook,
        hosts: hosts.length > 0 ? hosts : null,
        tags: selectedTags.length > 0 ? selectedTags : null,
        ask_password: true
    };

    try {
        const response = await fetch(`${API_BASE}/api/execute`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        currentExecutionId = data.execution_id;
        
        // Show execution card
        document.getElementById('execution-card').style.display = 'block';
        document.getElementById('execution-id').textContent = currentExecutionId;
        document.getElementById('execution-status').textContent = 'Running...';
        document.getElementById('execution-status').className = 'status-running';
        document.getElementById('execution-log').textContent = '';
        
        // Show cancel button, hide execute
        document.getElementById('execute-btn').style.display = 'none';
        document.getElementById('cancel-btn').style.display = 'block';
        
        // Start polling
        startPolling();
    } catch (error) {
        console.error('Error executing playbook:', error);
        alert(`Erro ao executar playbook: ${error.message}`);
    }
}

// Start polling execution status
function startPolling() {
    if (pollInterval) {
        clearInterval(pollInterval);
    }
    
    pollInterval = setInterval(async () => {
        if (!currentExecutionId) return;
        
        try {
            const response = await fetch(`${API_BASE}/api/executions/${currentExecutionId}`);
            const status = await response.json();
            
            // Update status
            const statusEl = document.getElementById('execution-status');
            statusEl.textContent = status.status.toUpperCase();
            statusEl.className = `status-${status.status}`;
            
            // Update log
            const logEl = document.getElementById('execution-log');
            if (status.stdout) {
                logEl.textContent = status.stdout;
            }
            if (status.stderr) {
                logEl.textContent += '\n[ERROR] ' + status.stderr;
            }
            
            // Scroll to bottom
            logEl.scrollTop = logEl.scrollHeight;
            
            // Check if finished
            if (['success', 'failed', 'cancelled'].includes(status.status)) {
                clearInterval(pollInterval);
                pollInterval = null;
                document.getElementById('execute-btn').style.display = 'block';
                document.getElementById('cancel-btn').style.display = 'none';
            }
        } catch (error) {
            console.error('Error polling status:', error);
        }
    }, 1000);
}

// Cancel execution
async function cancelExecution() {
    if (!currentExecutionId) return;
    
    try {
        const response = await fetch(`${API_BASE}/api/executions/${currentExecutionId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            if (pollInterval) {
                clearInterval(pollInterval);
                pollInterval = null;
            }
            document.getElementById('execution-status').textContent = 'CANCELLED';
            document.getElementById('execution-status').className = 'status-cancelled';
            document.getElementById('execute-btn').style.display = 'block';
            document.getElementById('cancel-btn').style.display = 'none';
        }
    } catch (error) {
        console.error('Error cancelling execution:', error);
        alert(`Erro ao cancelar execução: ${error.message}`);
    }
}


