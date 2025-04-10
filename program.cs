using CommandLine;
using DocXToPdfConverter;
using iText.Kernel.Pdf;
using iText.Kernel.Pdf.Canvas.Parser;
using iText.Kernel.Pdf.Canvas.Parser.Listener;
using System;
using System.IO;

public class Options
{
    [Option('i', "input", Required = true, HelpText = "Input Word file path")]
    public string InputPath { get; set; }

    [Option('o', "output", Required = true, HelpText = "Output PDF file path")]
    public string OutputPath { get; set; }

    [Option('p', "page-size", Default = "A4", HelpText = "Page size (A4, Letter, Legal)")]
    public string PageSize { get; set; }

    [Option('t', "orientation", Default = "Portrait", HelpText = "Page orientation (Portrait, Landscape)")]
    public string Orientation { get; set; }

    [Option("preserve-formatting", HelpText = "Preserve original formatting")]
    public bool PreserveFormatting { get; set; }

    [Option("optimize", HelpText = "Optimize PDF for web")]
    public bool Optimize { get; set; }
}

class Program
{
    static void Main(string[] args)
    {
        Parser.Default.ParseArguments<Options>(args)
            .WithParsed<Options>(options =>
            {
                try
                {
                    ConvertWordToPdf(options);
                    Console.WriteLine("Conversion completed successfully");
                    Environment.Exit(0);
                }
                catch (Exception ex)
                {
                    Console.Error.WriteLine($"Conversion failed: {ex.Message}");
                    Environment.Exit(1);
                }
            });
    }

    static void ConvertWordToPdf(Options options)
    {
        // Validate input file
        if (!File.Exists(options.InputPath))
        {
            throw new FileNotFoundException("Input file not found", options.InputPath);
        }

        // Convert Word to PDF using DocXToPdfConverter
        var converter = new DocXToPdfConverter.Converter();
        
        // Set conversion options
        var conversionOptions = new ConversionOptions
        {
            PageSize = GetPageSize(options.PageSize),
            PageOrientation = GetOrientation(options.Orientation),
            PreserveFormatting = options.PreserveFormatting
        };

        converter.Convert(options.InputPath, options.OutputPath, conversionOptions);

        // Apply PDF optimization if requested
        if (options.Optimize)
        {
            OptimizePdf(options.OutputPath);
        }
    }

    static PageSize GetPageSize(string size)
    {
        return size.ToLower() switch
        {
            "letter" => PageSize.Letter,
            "legal" => PageSize.Legal,
            _ => PageSize.A4,
        };
    }

    static PageOrientation GetOrientation(string orientation)
    {
        return orientation.ToLower() switch
        {
            "landscape" => PageOrientation.Landscape,
            _ => PageOrientation.Portrait,
        };
    }

    static void OptimizePdf(string pdfPath)
    {
        // Create a temporary file
        var tempPath = Path.GetTempFileName();

        try
        {
            // Create reader and writer with optimization settings
            var reader = new PdfReader(pdfPath);
            var writer = new PdfWriter(tempPath, new WriterProperties()
                .SetFullCompressionMode(true)
                .UseSmartMode());

            // Copy document with optimization
            var pdfDoc = new PdfDocument(reader, writer);
            pdfDoc.Close();

            // Replace original with optimized version
            File.Delete(pdfPath);
            File.Move(tempPath, pdfPath);
        }
        catch
        {
            if (File.Exists(tempPath))
            {
                File.Delete(tempPath);
            }
            throw;
        }
    }
}