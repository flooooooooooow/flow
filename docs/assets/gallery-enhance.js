/* Progressive enhancement for the existing docs/demos/*.md galleries.
 *
 * Their source stays as ordinary Markdown tables so GitHub renders it well.
 * On the Flow Wiki, alternating image/caption rows become the same responsive
 * cards used by the generated shader gallery and demo showcase.
 */
(function () {
    'use strict';

    var root = document.getElementById('markdownContent');
    if (!root) return;

    function onDemoPage() {
        var hash = String(window.location.hash || '');
        return hash.indexOf('demos/') !== -1;
    }

    function imageFromCell(cell) {
        return cell ? cell.querySelector('img') : null;
    }

    function enhanceTable(table) {
        if (table.dataset.demoEnhanced === '1') return;
        table.dataset.demoEnhanced = '1';

        var body = table.tBodies && table.tBodies.length ? table.tBodies[0] : null;
        if (!body) return;
        var rows = Array.prototype.slice.call(body.rows || []);
        if (rows.length < 2) return;

        var cards = [];
        for (var rowIndex = 0; rowIndex + 1 < rows.length; rowIndex += 2) {
            var mediaRow = rows[rowIndex];
            var captionRow = rows[rowIndex + 1];
            var mediaCells = Array.prototype.slice.call(mediaRow.cells || []);
            var captionCells = Array.prototype.slice.call(captionRow.cells || []);
            var imageCount = mediaCells.reduce(function (count, cell) {
                return count + (imageFromCell(cell) ? 1 : 0);
            }, 0);

            /* A normal data table may contain a logo or diagram. Gallery rows
             * are specifically image-dominant and followed by parallel captions. */
            if (!imageCount || captionCells.length !== mediaCells.length) {
                return;
            }

            mediaCells.forEach(function (mediaCell, column) {
                var img = imageFromCell(mediaCell);
                if (!img) return;
                var captionCell = captionCells[column];

                var figure = document.createElement('figure');
                figure.className = 'demo-tile';

                var media = document.createElement('div');
                media.className = 'demo-tile-media';
                var linked = mediaCell.querySelector('a');
                if (linked && linked.getAttribute('href')) {
                    var a = document.createElement('a');
                    a.className = 'demo-tile-media';
                    a.href = linked.getAttribute('href');
                    a.appendChild(img.cloneNode(true));
                    figure.appendChild(a);
                } else {
                    media.appendChild(img.cloneNode(true));
                    figure.appendChild(media);
                }

                var caption = document.createElement('figcaption');
                caption.innerHTML = captionCell.innerHTML;
                figure.appendChild(caption);
                cards.push(figure);
            });
        }

        if (!cards.length) return;
        var grid = document.createElement('div');
        grid.className = 'demo-tile-grid demo-tile-grid-enhanced';
        cards.forEach(function (card) { grid.appendChild(card); });

        var wrapper = table.parentElement && table.parentElement.classList.contains('table-wrap')
            ? table.parentElement
            : table;
        wrapper.replaceWith(grid);
    }

    function enhance() {
        if (!onDemoPage()) return;
        root.querySelectorAll('table').forEach(enhanceTable);
    }

    var scheduled = false;
    function schedule() {
        if (scheduled) return;
        scheduled = true;
        window.requestAnimationFrame(function () {
            scheduled = false;
            enhance();
        });
    }

    new MutationObserver(schedule).observe(root, { childList: true, subtree: true });
    window.addEventListener('hashchange', schedule);
    schedule();
})();
