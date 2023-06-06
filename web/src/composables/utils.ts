const downloadTSVFile = (filename: string, content: string) => {
  // credit: https://www.bitdegree.org/learn/javascript-download
  let element = document.createElement("a");
  element.setAttribute(
    "href",
    "data:text/tsv;charset=utf-8," + encodeURIComponent(content)
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

export { downloadTSVFile, truncate };
