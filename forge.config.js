module.exports = {
  packagerConfig: {
    asar: true,
    executableName: "CSVExtractor"
  },
  makers: [
    {
      name: "@electron-forge/maker-squirrel",
      config: {
        name: "CSVExtractor",
        authors: "CSV Extractor",
        description: "A local CSV extraction tool"
      }
    }
  ]
};
