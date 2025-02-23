async function fetchTranslation(){
    try {
        const response = await fetch('/data/');
        const data = await response.json();
        if (data.length > 0) {
            const lastEntry = data[data.length - 1];
            document.getElementById('original-text').value = lastEntry.original_text;
            document.getElementById('translated-text').value = lastEntry.translated_text;
        }
    } catch (error) {
        console.error('Ошибка при получении данных:', error);
    }
}

window.onload = fetchTranslation;