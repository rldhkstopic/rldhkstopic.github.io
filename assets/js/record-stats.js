/**
 * 기록 통계 — 연속 기록일수와 이번 달 집계
 *
 * 홈의 #daily-log-dates 에 박힌 기록 날짜 목록(YYYY-MM-DD)을 읽어 계산한다.
 * 나중에 경험치·레벨 같은 게임 요소를 붙일 때도 여기가 입력 지점이 된다.
 */
(function () {
  'use strict';

  var DAY = 86400000;

  /** 'YYYY-MM-DD' 를 현지 자정 기준 Date 로. (new Date('YYYY-MM-DD') 는 UTC 로 해석되어 하루씩 밀린다) */
  function parseDay(s) {
    var p = String(s).trim().split('-');
    if (p.length !== 3) return null;
    var d = new Date(+p[0], +p[1] - 1, +p[2]);
    return isNaN(d.getTime()) ? null : d;
  }

  function midnight(d) {
    return new Date(d.getFullYear(), d.getMonth(), d.getDate());
  }

  function daysBetween(a, b) {
    return Math.round((midnight(a) - midnight(b)) / DAY);
  }

  /**
   * 연속 기록일수.
   * 오늘 기록이 있으면 오늘부터, 없고 어제 기록이 있으면 어제부터 거슬러 센다.
   * (아직 오늘 기록을 안 했다고 해서 어제까지 쌓은 연속이 즉시 깨지지는 않게 한다)
   */
  function computeStreak(days, today) {
    if (!days.length) return { streak: 0, loggedToday: false, brokenAt: null };

    var set = {};
    days.forEach(function (d) { set[midnight(d).getTime()] = true; });

    var loggedToday = !!set[midnight(today).getTime()];
    var cursor = midnight(today);
    if (!loggedToday) {
      cursor = new Date(cursor.getTime() - DAY);
      if (!set[cursor.getTime()]) return { streak: 0, loggedToday: false, brokenAt: days[0] };
    }

    var streak = 0;
    while (set[cursor.getTime()]) {
      streak++;
      cursor = new Date(cursor.getTime() - DAY);
    }
    return { streak: streak, loggedToday: loggedToday, brokenAt: null };
  }

  function countThisMonth(days, today) {
    return days.filter(function (d) {
      return d.getFullYear() === today.getFullYear() && d.getMonth() === today.getMonth();
    }).length;
  }

  /** 상황에 맞는 한 줄. 다그치지 않고 상태만 알려준다. */
  function nudgeText(stat, days, today) {
    if (!days.length) return '첫 기록을 남겨보세요.';

    if (stat.loggedToday) {
      return stat.streak > 1
        ? '오늘 기록 완료 · ' + stat.streak + '일째 이어지는 중'
        : '오늘 기록 완료';
    }
    if (stat.streak > 0) {
      return stat.streak + '일 연속 기록 중 · 오늘은 아직입니다';
    }

    var gap = daysBetween(today, days[0]);
    if (gap <= 1) return '오늘은 아직 기록이 없습니다';
    if (gap < 30) return '마지막 기록에서 ' + gap + '일 지났습니다';
    return '마지막 기록: ' + days[0].getFullYear() + '. ' + (days[0].getMonth() + 1) + '. ' + days[0].getDate();
  }

  function init() {
    var el = document.getElementById('daily-log-dates');
    if (!el) return;

    var raw;
    try {
      raw = JSON.parse(el.textContent || '[]');
    } catch (e) {
      raw = [];
    }

    var days = raw.map(parseDay).filter(Boolean).sort(function (a, b) { return b - a; });
    var today = new Date();

    var stat = computeStreak(days, today);

    var streakEl = document.getElementById('record-streak');
    var monthEl = document.getElementById('record-month');
    var nudgeEl = document.getElementById('record-nudge');

    if (streakEl) streakEl.textContent = stat.streak;
    if (monthEl) monthEl.textContent = countThisMonth(days, today);
    if (nudgeEl) {
      nudgeEl.textContent = nudgeText(stat, days, today);
      nudgeEl.classList.toggle('dash-nudge-done', stat.loggedToday);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
