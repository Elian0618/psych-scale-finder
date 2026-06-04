async () => {
  const visibleCaptcha = (() => {
    const cap = document.querySelector("#tcaptcha_transform_dy");
    return !!(cap && cap.getBoundingClientRect().top >= 0);
  })();
  if (visibleCaptcha) {
    return {
      classification: "captcha",
      blocker: "CNKI captcha is visible. User must solve it in Chrome.",
      url: location.href,
    };
  }

  const linkRows = Array.from(document.querySelectorAll("a")).map((a, index) => {
    const text = (a.innerText || "").trim();
    const href = a.href || "";
    const id = a.id || "";
    const cls = String(a.className || "");
    const title = a.title || "";
    const haystack = [text, href, id, cls, title].join(" ");
    return { index, text, href, id, cls, title, haystack };
  });

  const downloads = linkRows.filter((row) =>
    /下载|PDF|pdf|CAJ|caj|DownDetail|download|bar\/download|在线阅读/.test(row.haystack)
  );

  const directPdf = downloads.find((row) =>
    /pdf/i.test(row.text) &&
    !/分页|分章|在线阅读/.test(row.text) &&
    !/downtype=downpage|downtype=catalog/i.test(row.href)
  );

  const fullCaj = downloads.find((row) => /CAJ整本下载|整本下载/.test(row.text));
  const pageDownload = downloads.find((row) => /分页下载/.test(row.text) || /downtype=downpage/i.test(row.href));
  const chapterDownload = downloads.find((row) => /分章下载/.test(row.text) || /downtype=catalog/i.test(row.href));
  const onlineRead = downloads.find((row) => /在线阅读/.test(row.text));

  let classification = "no_fulltext";
  let preferredAction = "report_no_download_link";
  let preferredLink = null;

  if (directPdf) {
    classification = "direct_pdf";
    preferredAction = "download_direct_pdf";
    preferredLink = directPdf;
  } else if (fullCaj) {
    classification = "full_caj_only";
    preferredAction = "download_full_caj_then_convert";
    preferredLink = fullCaj;
  } else if (pageDownload) {
    classification = "page_caj_only";
    preferredAction = "open_page_download_then_download_likely_appendix_range";
    preferredLink = pageDownload;
  } else if (chapterDownload) {
    classification = "chapter_caj_only";
    preferredAction = "open_chapter_download_then_download_likely_appendix_chapter";
    preferredLink = chapterDownload;
  } else if (onlineRead) {
    classification = "online_read_only";
    preferredAction = "use_online_reading_only_after_pdf_and_caj_fail";
    preferredLink = onlineRead;
  }

  const downloadText =
    (document.body.innerText || "").match(/手机阅读[\s\S]*?(下载：|页数：|大小：)[^\n]*(?:\n[^\n]*){0,4}/)?.[0] ||
    "";

  return {
    classification,
    preferredAction,
    preferredLink,
    hasDirectPdf: !!directPdf,
    hasFullCaj: !!fullCaj,
    hasPageDownload: !!pageDownload,
    hasChapterDownload: !!chapterDownload,
    hasOnlineRead: !!onlineRead,
    downloadText,
    title: document.title,
    url: location.href,
    downloads: downloads.map(({ haystack, ...row }) => row),
  };
}
