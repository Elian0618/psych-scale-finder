async () => {
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const visible = (el) => {
    if (!el) return false;
    const style = getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    return (
      style.display !== "none" &&
      style.visibility !== "hidden" &&
      Number(style.opacity || 1) > 0 &&
      rect.width > 0 &&
      rect.height > 0 &&
      rect.bottom > 0 &&
      rect.top < innerHeight
    );
  };
  const waitFor = async (predicate, timeoutMs = 45000) => {
    const started = Date.now();
    while (Date.now() - started < timeoutMs) {
      if (predicate()) return true;
      await sleep(500);
    }
    return false;
  };

  const pageReady = await waitFor(
    () => document.querySelector(".brief h1") || /下载|摘要|关键词/.test(document.body?.innerText || "")
  );
  const bodyText = document.body?.innerText || "";
  const title =
    document.querySelector(".brief h1")?.innerText?.trim()
      ?.replace(/\s*附视频\s*$/, "")
      ?.replace(/\s*网络首发\s*$/, "") || document.title;

  if (!pageReady) {
    return {
      classification: "page_not_ready",
      preferredAction: "reload_or_report_cnki_page_not_ready",
      title,
      url: location.href,
      bodyHint: bodyText.slice(0, 500),
    };
  }

  const cap = document.querySelector("#tcaptcha_transform_dy");
  if (visible(cap)) {
    return {
      classification: "captcha",
      preferredAction: "ask_user_to_solve_captcha",
      blocker: "CNKI captcha is visible. User must solve it in Chrome.",
      title,
      url: location.href,
    };
  }

  const notLogged =
    document.querySelector(".downloadlink.icon-notlogged") ||
    document.querySelector('[class*="notlogged"]');
  if (notLogged || (/请先登录/.test(bodyText) && !document.querySelector("#pdfDown") && !document.querySelector("#cajDown"))) {
    return {
      classification: "login_needed",
      preferredAction: "ask_user_to_login",
      blocker: "CNKI login is required for download.",
      title,
      url: location.href,
    };
  }

  const linkRows = Array.from(document.querySelectorAll("a")).map((a, index) => {
    const text = (a.innerText || "").trim();
    const href = a.href || "";
    const id = a.id || "";
    const cls = String(a.className || "");
    const titleAttr = a.title || "";
    const haystack = [text, href, id, cls, titleAttr].join(" ");
    return { index, text, href, id, cls, title: titleAttr, haystack };
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

  const accessBlocked =
    /没有权限|暂无权限|未订购|机构未订购|购买|充值/.test(bodyText) &&
    !directPdf &&
    !fullCaj &&
    !pageDownload &&
    !chapterDownload;
  if (accessBlocked) {
    return {
      classification: "access_blocked",
      preferredAction: "report_cnki_access_blocked",
      blocker: "No CNKI institutional/download access detected.",
      title,
      url: location.href,
      downloads: downloads.map(({ haystack, ...row }) => row),
    };
  }

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
    bodyText.match(/手机阅读[\s\S]*?(下载：|页数：|大小：)[^\n]*(?:\n[^\n]*){0,4}/)?.[0] || "";

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
    title,
    url: location.href,
    downloads: downloads.map(({ haystack, ...row }) => row),
  };
}
