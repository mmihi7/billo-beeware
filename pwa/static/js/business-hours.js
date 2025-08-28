// Business Hours Management
document.addEventListener('DOMContentLoaded', function() {
    // Days of the week in order
    const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
    
    // Format time from 'HH:MM:SS' to 'HH:MM'
    function formatTime(timeStr) {
        if (!timeStr) return '';
        return timeStr.split(':').slice(0, 2).join(':');
    }

    // Load business hours
    async function loadBusinessHours() {
        try {
            const response = await fetch('/api/business-hours');
            const data = await response.json();
            
            // Update the business hours table
            const tbody = document.getElementById('businessHoursTable');
            if (tbody) {
                tbody.innerHTML = '';
                
                days.forEach(day => {
                    const hours = data[day] || [null, null];
                    const row = document.createElement('tr');
                    
                    // Determine status
                    const now = new Date();
                    const currentDay = days[now.getDay() === 0 ? 6 : now.getDay() - 1]; // Adjust for Sunday
                    const isToday = day === currentDay;
                    let status = 'Closed';
                    let statusClass = 'text-danger';
                    
                    if (hours[0] && hours[1]) {
                        const [openHour, openMinute] = hours[0].split(':');
                        const [closeHour, closeMinute] = hours[1].split(':');
                        
                        const openTime = new Date();
                        openTime.setHours(parseInt(openHour), parseInt(openMinute), 0);
                        
                        const closeTime = new Date();
                        closeTime.setHours(parseInt(closeHour), parseInt(closeMinute), 0);
                        
                        if (isToday) {
                            if (now >= openTime && now <= closeTime) {
                                status = 'Open Now';
                                statusClass = 'text-success';
                            } else if (now < openTime) {
                                status = `Opens at ${formatTime(hours[0])}`;
                            } else {
                                status = `Closed for Today`;
                            }
                        } else {
                            status = `${formatTime(hours[0])} - ${formatTime(hours[1])}`;
                            statusClass = '';
                        }
                    }
                    
                    row.innerHTML = `
                        <td>${day.charAt(0).toUpperCase() + day.slice(1)}</td>
                        <td>${hours[0] ? formatTime(hours[0]) : 'Closed'}</td>
                        <td>${hours[1] ? formatTime(hours[1]) : 'Closed'}</td>
                        <td class="${statusClass}">${status}</td>
                    `;
                    tbody.appendChild(row);
                });
            }
            
            // Populate the edit form
            const formBody = document.getElementById('businessHoursFormBody');
            if (formBody) {
                formBody.innerHTML = '';
                
                days.forEach(day => {
                    const hours = data[day] || ['09:00', '17:00'];
                    const row = document.createElement('tr');
                    
                    row.innerHTML = `
                        <td>${day.charAt(0).toUpperCase() + day.slice(1)}</td>
                        <td>
                            <input type="time" class="form-control" name="${day}-open" 
                                   value="${hours[0] || ''}" ${!hours[0] ? 'disabled' : ''}>
                        </td>
                        <td>
                            <input type="time" class="form-control" name="${day}-close" 
                                   value="${hours[1] || ''}" ${!hours[1] ? 'disabled' : ''}>
                        </td>
                        <td class="text-center">
                            <div class="form-check form-switch">
                                <input class="form-check-input day-toggle" type="checkbox" 
                                       data-day="${day}" ${hours[0] ? 'checked' : ''}>
                            </div>
                        </td>
                    `;
                    formBody.appendChild(row);
                });
                
                // Add event listeners for day toggles
                document.querySelectorAll('.day-toggle').forEach(toggle => {
                    toggle.addEventListener('change', function() {
                        const day = this.dataset.day;
                        const row = this.closest('tr');
                        const openInput = row.querySelector(`[name="${day}-open"]`);
                        const closeInput = row.querySelector(`[name="${day}-close"]`);
                        
                        if (this.checked) {
                            openInput.disabled = false;
                            closeInput.disabled = false;
                            if (!openInput.value) openInput.value = '09:00';
                            if (!closeInput.value) closeInput.value = '17:00';
                        } else {
                            openInput.disabled = true;
                            closeInput.disabled = true;
                            openInput.value = '';
                            closeInput.value = '';
                        }
                    });
                });
            }
            
        } catch (error) {
            console.error('Error loading business hours:', error);
            alert('Failed to load business hours');
        }
    }
    
    // Save business hours
    async function saveBusinessHours() {
        try {
            const form = document.getElementById('businessHoursForm');
            const formData = new FormData(form);
            const hoursData = {};
            
            days.forEach(day => {
                const open = formData.get(`${day}-open`);
                const close = formData.get(`${day}-close`);
                
                if (open && close) {
                    hoursData[day] = [open, close];
                } else {
                    hoursData[day] = [null, null];
                }
            });
            
            const response = await fetch('/api/business-hours', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(hoursData)
            });
            
            if (response.ok) {
                // Reload the business hours
                await loadBusinessHours();
                // Close the modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('editBusinessHoursModal'));
                if (modal) modal.hide();
            } else {
                throw new Error('Failed to save business hours');
            }
        } catch (error) {
            console.error('Error saving business hours:', error);
            alert('Failed to save business hours');
        }
    }
    
    // Event listeners
    const saveBtn = document.getElementById('saveBusinessHours');
    if (saveBtn) {
        saveBtn.addEventListener('click', saveBusinessHours);
    }
    
    // Load business hours when the tab is shown
    const businessHoursTab = document.querySelector('a[href="#business-hours"]');
    if (businessHoursTab) {
        businessHoursTab.addEventListener('shown.bs.tab', loadBusinessHours);
    }
    
    // Load business hours if we're on the business hours tab
    if (window.location.hash === '#business-hours') {
        loadBusinessHours();
    }
});
