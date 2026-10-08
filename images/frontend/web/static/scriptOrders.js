function getOrders() {
    fetch('/api/orders', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include'
    })
    .then(response => {
        if (!response.ok) throw new Error('Failed to load orders');
        return response.json();
    })
    .then(data => {
        console.log(data);
        var tbody = document.querySelector('#orders-list tbody');
        tbody.innerHTML = '';

        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No orders found</td></tr>';
            return;
        }

        data.forEach(function (order, idx) {
            // Main row
            var row = document.createElement('tr');
            row.className = 'order-row';
            row.setAttribute('data-order-idx', idx);
            row.innerHTML =
                '<td>' + order.id + '</td>' +
                '<td>' + esc(order.user_name) + '</td>' +
                '<td>' + esc(order.user_email) + '</td>' +
                '<td>$' + order.total.toFixed(2) + '</td>' +
                '<td>' + esc(order.status) + '</td>' +
                '<td>' + new Date(order.created_at).toLocaleString() + '</td>';
            row.addEventListener('click', function () { toggleDetail(idx); });
            tbody.appendChild(row);

            // Detail row (hidden by default)
            var detailRow = document.createElement('tr');
            detailRow.className = 'detail-row';
            detailRow.id = 'order-detail-' + idx;
            detailRow.style.display = 'none';
            var itemsHtml = '<div class="p-3">' +
                '<h6>Products</h6>' +
                '<table class="table table-sm table-bordered items-table">' +
                '<thead><tr>' +
                '<th>Product</th><th>Unit Price</th><th>Qty</th><th>Subtotal</th>' +
                '</tr></thead><tbody>';

            order.items.forEach(function (item) {
                itemsHtml +=
                    '<tr>' +
                    '<td>' + esc(item.product_name) + ' (#' + item.product_id + ')</td>' +
                    '<td>$' + item.unit_price.toFixed(2) + '</td>' +
                    '<td>' + item.quantity + '</td>' +
                    '<td>$' + item.subtotal.toFixed(2) + '</td>' +
                    '</tr>';
            });

            itemsHtml += '</tbody></table></div>';
            detailRow.innerHTML = '<td colspan="6">' + itemsHtml + '</td>';
            tbody.appendChild(detailRow);
        });
    })
    .catch(function (error) {
        console.error('Error:', error);
    });
}

function toggleDetail(idx) {
    var detailRow = document.getElementById('order-detail-' + idx);
    if (detailRow) {
        detailRow.style.display = (detailRow.style.display === 'none') ? '' : 'none';
    }
}

function esc(str) {
    if (!str) return '';
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
}
