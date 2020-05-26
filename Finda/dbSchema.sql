CREATE TABLE AssetClass (
    AssetClassName TEXT PRIMARY KEY
);

CREATE TABLE Asset (
    AssetTicker TEXT PRIMARY KEY,
    Name TEXT,
    AssetClassName TEXT,
    FOREIGN KEY(AssetClassName) REFERENCES AssetClass(AssetClassName) ON DELETE CASCADE
);

CREATE TABLE AssetValue (
    AssetTicker TEXT,
    ADate TEXT,
    AOpen TEXT,
    AClose TEXT,
    ALow TEXT,
    AHigh TEXT,
    IsInterpolated INTEGER,
    FOREIGN KEY(AssetTicker) REFERENCES Asset(AssetTicker) ON DELETE CASCADE
    PRIMARY KEY (AssetTicker, ADate)
);

CREATE TABLE DividendPayout(
  AssetTicker TEXT,
  PDate TEXT,
  Payout TEXT,
  FOREIGN KEY(AssetTicker) REFERENCES Asset(AssetTicker) ON DELETE CASCADE
  PRIMARY KEY (AssetTicker, PDate)
);

CREATE INDEX UX_DividendPayout_AssetTicker ON DividendPayout(AssetTicker);
CREATE INDEX IX_Asset_AssetClass ON Asset(AssetClassName);
CREATE INDEX UX_Values_AssetTicker ON AssetValue(AssetTicker);
CREATE INDEX UX_Value_Date_AssetTicker ON AssetValue(AssetTicker, ADate);
CREATE INDEX IX_Values_IsInterpolated ON AssetValue(IsInterpolated);




