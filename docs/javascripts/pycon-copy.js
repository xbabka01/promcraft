// Make the copy button on `>>>` examples copy only the code, without the
// prompts and the expected output, so it can be pasted into a script. The
// theme copies the nearest `data-copy` attribute in place of the block's text.
// `document$` emits on every page load, including instant navigation.
document$.subscribe(() => {
  for (const code of document.querySelectorAll(".highlight code")) {
    const lines = code.textContent.split("\n");
    if (!lines.find((line) => line.trim())?.startsWith(">>>")) continue;

    const source = [];
    for (const line of lines) {
      const prompt = line.match(/^(>>>|\.\.\.)( |$)/);
      if (prompt) source.push(line.slice(prompt[0].length));
      else if (!line.trim()) source.push(""); // keep the gaps between examples
    }
    code.dataset.copy = source.join("\n").replace(/\n{3,}/g, "\n\n").trim();
  }
});
