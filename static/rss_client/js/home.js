let currentGroupId = null;
const DOMAIN_NAME = window.location.origin;

// Check if user is authenticated
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = `${window.location.origin}/accounts/signin`;
    }
}

// Fetch UID and display it
async function fetchUID() {
    try {
        const response = await fetch(`${DOMAIN_NAME}/api/v1/accounts/uid`, {
            headers: {
                'Authorization': `Token ${localStorage.getItem('token')}`
            }
        });

        const result = await response.json();
        if (response.ok) {
            document.getElementById('uid').textContent = result.payload;
            localStorage.setItem('uid', result.payload);
        } else {
            console.error(result);
            alert('تعذر جلب UID');
        }
    } catch (error) {
        console.error('Error fetching UID:', error);
    }
}

// Fetch groups and sources for the user
async function fetchGroupsAndSources() {
    try {
        const response = await fetch(`${DOMAIN_NAME}/api/v1/groups/`, {
            headers: {
                'Authorization': `Token ${localStorage.getItem('token')}`
            }
        });

        const result = await response.json();
        if (response.ok) {
            result.payload.forEach(group => addGroupToPage(group));
        } else {
            console.error(result);
            alert('تعذر جلب المجموعات');
        }
    } catch (error) {
        console.error('Error fetching groups and sources:', error);
    }
}

// Handle adding groups
document.getElementById('add-group-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const groupName = document.getElementById('group-name').value;
    try {
        const response = await fetch(`${DOMAIN_NAME}/api/v1/groups/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ name: groupName })
        });

        const result = await response.json();
        if (result.success) {
            addGroupToPage(result.payload);
            document.getElementById('add-group-form').reset();
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error('Error adding group:', error);
    }
});
document.getElementById('news-summary-btn').addEventListener('click', async () => {
    const uid = localStorage.getItem('uid');
    // print local storage
    console.log(localStorage);
    if (!uid) {
        alert('لم يتم العثور على UID');
        return;
    }

    try {
        const response = await fetch(`${DOMAIN_NAME}/api/v1/news/summary/${uid}`, {
            headers: {
                'Authorization': `Token ${localStorage.getItem('token')}`
            }
        });

        const xmlText = await response.text();
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(xmlText, "text/xml");
        const items = xmlDoc.getElementsByTagName('item');
        
        const newsList = document.getElementById('news-list');
        newsList.innerHTML = ''; // Clear existing items

        Array.from(items).forEach(item => {
            const title = item.getElementsByTagName('title')[0]?.textContent || '';
            let description = item.getElementsByTagName('description')[0]?.textContent || '';
            const pubDate = item.getElementsByTagName('pubDate')[0]?.textContent || '';
            const link = item.getElementsByTagName('link')[0]?.textContent || '';

            // Clean up CDATA and decode HTML entities in description
            description = description.replace('<![CDATA[', '').replace(']]>', '');
            description = new DOMParser().parseFromString(description, 'text/html').body.textContent;

            const newsItem = document.createElement('div');
            newsItem.className = 'list-group-item';
            newsItem.innerHTML = `
                <div class="d-flex w-100 justify-content-between">
                    <h5 class="mb-1">${title}</h5>
                    <small class="text-muted">${new Date(pubDate)} | ${new Date(pubDate).toLocaleDateString('ar-SA')}</small>
                </div>
                <p class="mb-1">${description}</p>
                <small class="text-muted">
                    <a href="${link}" target="_blank" class="text-decoration-none">اقرأ المزيد</a>
                </small>
            `;
            newsList.appendChild(newsItem);
        });

        // Show the modal
        const modal = new bootstrap.Modal(document.getElementById('newsSummaryModal'));
        modal.show();
    } catch (error) {
        console.error('Error fetching news summary:', error);
        alert('حدث خطأ أثناء جلب ملخص الأخبار');
    }
});
// Render groups dynamically
function addGroupToPage(group) {
    const groupBlock = document.createElement('div');
    groupBlock.className = 'col-md-4';
    groupBlock.innerHTML = `
        <div class="card h-100">
            <div class="card-body">
                <h5 class="card-title d-flex justify-content-between align-items-center">
                    ${group.name}
                    <button class="btn btn-danger btn-sm" onclick="deleteGroup(${group.id})">حذف</button>
                </h5>
                <button class="btn btn-outline-primary btn-sm" data-bs-toggle="modal" data-bs-target="#addSourceModal" onclick="setCurrentGroupId(${group.id})">إضافة مصدر</button>
                <ul class="list-group mt-3" id="sources-list-${group.id}">
                    <li class="list-group-item text-muted">جاري تحميل المصادر...</li>
                </ul>
            </div>
        </div>
    `;
    document.getElementById('groups').appendChild(groupBlock);
    fetchSourcesForGroup(group.id); // Fetch and display sources for this group
}

async function showSourceDetails(sourceId, page = 1, size = 5) {
    try {
        const response = await fetch(`${DOMAIN_NAME}/api/v1/sources/${sourceId}?page=${page}&size=${size}`, {
            headers: {
                'Authorization': `Token ${localStorage.getItem('token')}`
            },
            method: 'GET'
        });

        const result = await response.json();
        if (result.success) {
            const source = result.payload.data;
            const pagination = result.payload.pagination;

            // Create the modal dynamically if it doesn't exist
            let sourceDetailsModal = document.getElementById('sourceDetailsModal');
            if (!sourceDetailsModal) {
                sourceDetailsModal = document.createElement('div');
                sourceDetailsModal.id = 'sourceDetailsModal';
                sourceDetailsModal.className = 'modal fade';
                sourceDetailsModal.innerHTML = `
            <div class="modal-dialog modal-xl"> <!-- Make the modal wider -->
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">تفاصيل المصدر</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-4">
                                <p><strong>عنوان المصدر:</strong> <span id="source-name"></span></p>
                                <p><strong>تاريخ المصدر:</strong> <span id="source-date"></span></p>
                                <p><strong>رابط المصدر:</strong> <span id="source-link"></span></p>
                            </div>
                            <div class="col-md-8">
                                <h6 class="mt-3">اﻷخبار</h6>
                                <div id="source-feeds" class="list-group" style="max-height: 400px; overflow-y: auto;"></div>
                                <nav aria-label="Page navigation">
                                    <ul class="pagination justify-content-center mt-3" id="pagination-controls"></ul>
                                </nav>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
                document.body.appendChild(sourceDetailsModal);
            }

            // Populate modal content
            document.getElementById('source-name').textContent = source.name;
            document.getElementById('source-url').textContent = source.url;
            document.getElementById('source-date').textContent = source.created_at;
            document.getElementById('source-link').innerHTML = `<a href="${source.url}" target="_blank">${source.url}</a>`;

            // Populate feeds
            const feedsList = document.getElementById('source-feeds');
            feedsList.innerHTML = ''; // Clear previous feeds
            source.feeds.forEach(feed => {
                const feedItem = document.createElement('a');
                feedItem.className = 'list-group-item list-group-item-action';
                feedItem.href = feed.url;
                feedItem.target = '_blank';
                feedItem.innerHTML = `
            <div class="d-flex w-100 justify-content-between">
                <h5 class="mb-1">${feed.title}</h5>
            </div>
            <p class="mb-1">${feed.description}</p>
                <div>
                    <small>
                        ${feed.tags.map(tag =>
                    `<span class="badge bg-primary text-light p-2 m-1">${tag}</span>`
                ).join('')}
                    </small>
                </div>
            <small>${feed.created_at}</small>
        `;
                feedsList.appendChild(feedItem);
            });

            // Populate pagination controls
            const paginationControls = document.getElementById('pagination-controls');
            paginationControls.innerHTML = ''; // Clear previous pagination controls
            for (let i = 1; i <= pagination.total_pages; i++) {
                const pageItem = document.createElement('li');
                pageItem.className = `page-item ${i === page ? 'active' : ''}`;
                pageItem.innerHTML = `<a class="page-link" href="#" onclick="showSourceDetails(${sourceId}, ${i})">${i}</a>`;
                paginationControls.appendChild(pageItem);
            }

            // Remove existing modal backdrops
            const backdrops = document.querySelectorAll('.modal-backdrop');
            backdrops.forEach(backdrop => backdrop.remove());

            // Show the modal
            const modal = new bootstrap.Modal(sourceDetailsModal);
            modal.show();
        } else {
            alert('تعذر جلب تفاصيل المصدر');
        }
    } catch (error) {
        console.error('Error fetching source details:', error);
        alert('حدث خطأ أثناء جلب تفاصيل المصدر');
    }
}

// Fetch and display sources for a specific group
async function fetchSourcesForGroup(groupId) {
    try {
        const response = await fetch(`${DOMAIN_NAME}/api/v1/groups/${groupId}`, {
            headers: {
                'Authorization': `Token ${localStorage.getItem('token')}`
            }
        });

        const result = await response.json();
        const sourcesList = document.getElementById(`sources-list-${groupId}`);
        sourcesList.innerHTML = ''; // Clear loading message

        if (response.ok) {
            if (result.payload.sources.length > 0) {
                result.payload.sources.forEach(source => {
                    const listItem = document.createElement('li');
                    listItem.className = 'list-group-item d-flex justify-content-between align-items-center';

                    // Create a clickable span for the source name
                    const sourceNameSpan = document.createElement('span');
                    sourceNameSpan.textContent = source.name;
                    sourceNameSpan.style.cursor = 'pointer';
                    sourceNameSpan.style.textDecoration = 'underline'; // Add underline
                    sourceNameSpan.classList.add('text-primary'); // Optional: add color to indicate clickability
                    sourceNameSpan.onclick = () => showSourceDetails(source.id);
                    listItem.appendChild(sourceNameSpan);

                    // Create delete button
                    const deleteButton = document.createElement('button');
                    deleteButton.className = 'btn btn-danger btn-sm';
                    deleteButton.textContent = 'حذف';
                    deleteButton.onclick = () => deleteSource(source.id, groupId);

                    listItem.appendChild(deleteButton);
                    sourcesList.appendChild(listItem);
                });
            } else {
                sourcesList.innerHTML = '<li class="list-group-item text-muted">لا توجد مصادر مضافة بعد.</li>';
            }
        } else {
            console.error(result);
            sourcesList.innerHTML = '<li class="list-group-item text-danger">تعذر جلب المصادر.</li>';
        }
    } catch (error) {
        console.error('Error fetching sources for group:', error);
        const sourcesList = document.getElementById(`sources-list-${groupId}`);
        sourcesList.innerHTML = '<li class="list-group-item text-danger">حدث خطأ أثناء تحميل المصادر.</li>';
    }
}
async function deleteSource(sourceId, groupId) {
    if (!confirm('هل أنت متأكد أنك تريد حذف هذا المصدر؟')) return;

    try {
        const response = await fetch(`${DOMAIN_NAME}/api/v1/sources/${sourceId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Token ${localStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            fetchSourcesForGroup(groupId); // Refresh sources for the group after deletion
            alert('تم حذف المصدر بنجاح');
        } else {
            alert('تعذر حذف المصدر');
        }
    } catch (error) {
        console.error('Error deleting source:', error);
    }
}


async function deleteGroup(groupId) {
    if (!confirm('هل أنت متأكد أنك تريد حذف هذه المجموعة؟')) return;

    try {
        const response = await fetch(`${DOMAIN_NAME}/api/v1/groups/${groupId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Token ${localStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            document.getElementById('groups').innerHTML = '';
            fetchGroupsAndSources(); // Refresh groups after deletion
            alert('تم حذف المجموعة بنجاح');
        } else {
            alert('تعذر حذف المجموعة');
        }
    } catch (error) {
        console.error('Error deleting group:', error);
    }
}

async function deleteSource(sourceId, groupId) {
    if (!confirm('هل أنت متأكد أنك تريد حذف هذا المصدر؟')) return;

    try {
        const response = await fetch(`${DOMAIN_NAME}/api/v1/sources/${sourceId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Token ${localStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            fetchSourcesForGroup(groupId); // Refresh sources for the group after deletion
            alert('تم حذف المصدر بنجاح');
        } else {
            alert('تعذر حذف المصدر');
        }
    } catch (error) {
        console.error('Error deleting source:', error);
    }
}

// Set current group ID when opening modal
function setCurrentGroupId(groupId) {
    currentGroupId = groupId;
}

// Handle adding source
document.getElementById('add-source-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const sourceUrl = document.getElementById('source-url').value;
    try {
        const response = await fetch(`${DOMAIN_NAME}/api/v1/sources/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ group_id: currentGroupId, url: sourceUrl })
        });

        const result = await response.json();
        if (result.success) {
            alert('تم إضافة المصدر بنجاح');
            document.getElementById('add-source-form').reset();
            const modal = bootstrap.Modal.getInstance(document.getElementById('addSourceModal'));
            modal.hide();
            fetchSourcesForGroup(currentGroupId); // Update sources list for the current group
        }
        else {
            alert(result.message);
        }
    } catch (error) {
        console.error('Error adding source:', error);
    }
});

// Handle logout
document.getElementById('logout-button').addEventListener('click', async () => {
    try {
        const response = await fetch(`${DOMAIN_NAME}/api/v1/accounts/logout`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${localStorage.getItem('token')}`,
                'X-CSRFToken': getCookie('csrftoken') // Ensure you include the CSRF token
            }
        });
        const result = await response.json();
        if (result.success) {
            alert('تم تسجيل الخروج بنجاح');
            window.location.href = `${DOMAIN_NAME}/accounts/signin`; // Redirect to sign-in page
            // Clear token and other user data
            localStorage.removeItem('token');
        } else {
            alert('فشل تسجيل الخروج');
        }
    } catch (error) {
        console.error('Error logging out:', error);
        alert('حدث خطأ أثناء تسجيل الخروج');
    }
});

document.getElementById('update-news-btn').addEventListener('click', async function() {
    const button = this;
    const btnText = document.getElementById('btn-text');
    const spinner = document.getElementById('loading-spinner');
    const statusDiv = document.getElementById('update-status');

    // Disable button and show spinner
    button.disabled = true;
    spinner.classList.remove('d-none');
    btnText.textContent = 'جاري التحديث...';
    statusDiv.textContent = '';

    try {
        const response = await fetch(`${DOMAIN_NAME}/api/v1/news/`, {
            method: 'GET',
            headers: {
                'Authorization': `Token ${localStorage.getItem('token')}`
            }
        });

        const result = await response.json();
        
        if (result.success) {
            alert('تم تحديث اﻷخبار بنجاح');
        } else {
            alert('تعذر تحديث اﻷخبار');
            statusDiv.classList.remove('text-success');
            statusDiv.classList.add('text-danger');
        }
    } catch (error) {
        console.error('Error updating news:', error);
        alert('حدث خطأ أثناء تحديث اﻷخبار');
    } finally {
        // Re-enable button and hide spinner
        button.disabled = false;
        spinner.classList.add('d-none');
        btnText.textContent = 'تحديث اﻷخبار';
    }
});


// Function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize UID fetch and groups/sources fetch
fetchUID();
fetchGroupsAndSources();