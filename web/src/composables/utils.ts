const downloadFile = (filename: string, content: string, contentType: string="text/tsv") => {
  // credit: https://www.bitdegree.org/learn/javascript-download
  let element = document.createElement("a");
  element.setAttribute(
    "href",
    "data:" + contentType + ";charset=utf-8," + encodeURIComponent(content)
  );
  element.setAttribute("download", filename);

  element.style.display = "none";
  document.body.appendChild(element);

  element.click();
  document.body.removeChild(element);
};

function truncate(str: string, n: number) {
  return str.length > n ? str.slice(0, n - 1) + "..." : str;
}

export { downloadFile, truncate };
