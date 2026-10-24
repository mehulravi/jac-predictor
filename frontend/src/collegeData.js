// College reference data. Figures (fees, packages) vary across aggregator
// sites year to year -- these are representative approximate figures as of
// mid-2026, cross-checked against multiple sources (NIRF 2025 filings,
// official fee circulars, recent public placement reports) after an
// earlier pass mistakenly used a partial/first-year fee figure as if it
// were the 4-year total. Always point students to the official website
// for exact, current numbers rather than treating these as final.

export const COLLEGES = {
  DTU: {
    shortCode: 'DTU',
    name: 'Delhi Technological University',
    website: 'https://www.dtu.ac.in',
    howToReach: {
      address: 'Shahbad Daulatpur, Main Bawana Road, Rohini, Delhi – 110042',
      details: [
        'Nearest metro: Samaypur Badli (Yellow Line), roughly 2.8 km from campus',
        'DTC bus routes 116, 130, 165, 215 stop near the Delhi Engineering College gate',
        'About 32 km from Indira Gandhi International Airport',
      ],
    },
    ranking: {
      source: 'NIRF 2025',
      items: [
        { label: 'Engineering', value: '#30' },
        { label: 'Overall', value: '#62' },
        { label: 'University', value: '#42' },
        { label: 'State Public University', value: '#13' },
      ],
    },
    fees: {
      tuition: '≈ ₹10–11 lakh total (4-year B.Tech; fee rises each year, roughly ₹2.3L → ₹2.7L)',
      hostel: '≈ ₹35,000–90,000 per year (mess ≈ ₹34,800/yr + room, varies by hostel type)',
    },
    placement: {
      note: 'Figures vary by branch and year — treat as indicative, not guaranteed.',
      companiesVisited: '300+ recruiters visit annually',
      highest: '≈ ₹85 LPA domestic (Atlassian); international offers have gone well above ₹1 Cr',
      average: '≈ ₹12–15 LPA typical range',
      recruiters: ['Google', 'Microsoft', 'Atlassian', 'Apple', 'Amazon', 'PwC', 'Deloitte'],
    },
  },

  NSUT: {
    shortCode: 'NSUT',
    name: 'Netaji Subhas University of Technology',
    website: 'https://www.nsut.ac.in',
    howToReach: {
      address: 'Sector-3, Dwarka, New Delhi – 110078',
      details: [
        'About 1 km from Dwarka Sector-3/Dwarka metro stations (Blue Line)',
        'Well connected by DTC buses and autos along Dwarka\'s main roads',
        'About 12 km from Indira Gandhi International Airport',
      ],
    },
    ranking: {
      source: 'NIRF 2025',
      items: [
        { label: 'Engineering', value: '#70' },
        { label: 'State Public University', value: '#39' },
      ],
    },
    fees: {
      tuition: '≈ ₹10–12 lakh total (4-year B.Tech; fee rises each year, roughly ₹2.2L → ₹2.9L)',
      hostel: '≈ ₹34,000–50,000 per year',
    },
    placement: {
      note: 'Figures vary by branch and year — treat as indicative, not guaranteed.',
      companiesVisited: 'National and global recruiters visit every season',
      highest: '≈ ₹65 LPA typical top offer; standout years have seen well above ₹1 Cr',
      average: '≈ ₹16–17 LPA typical range',
      recruiters: ['Apple', 'Google', 'DE Shaw', 'Zomato', 'Microsoft', 'Flipkart'],
    },
  },

  IIITD: {
    shortCode: 'IIIT-D',
    name: 'Indraprastha Institute of Information Technology Delhi',
    website: 'https://www.iiitd.ac.in',
    howToReach: {
      address: 'Okhla Industrial Estate, Phase III, New Delhi – 110020',
      details: [
        'About 1 km from Govind Puri metro station (Violet Line / Pink Line)',
        'Close to Nehru Place; roughly 5 km from Hazrat Nizamuddin Railway Station',
        'About 17 km from Indira Gandhi International Airport',
      ],
    },
    ranking: {
      source: 'NIRF 2025',
      items: [
        { label: 'Engineering', value: '#63' },
        { label: 'University', value: '#100' },
      ],
    },
    fees: {
      tuition: '≈ ₹19–20 lakh total (4-year B.Tech — IIIT-D is self-financed, notably higher than DTU/NSUT)',
      hostel: '≈ ₹1–1.2 lakh per year (mess + room, approximate)',
    },
    placement: {
      note: 'Figures vary by branch and year — treat as indicative, not guaranteed.',
      companiesVisited: '207 companies visited in 2025, making 769 offers (≈88% placement rate)',
      highest: '≈ ₹51 LPA domestic, ≈ ₹99 LPA for an overseas offer (2025 report)',
      average: '≈ ₹19–21 LPA typical range',
      recruiters: ['Microsoft', 'Google', 'Amazon', 'Adobe', 'Goldman Sachs', 'Qualcomm'],
    },
  },

  IGDTUW: {
    shortCode: 'IGDTUW',
    name: 'Indira Gandhi Delhi Technical University for Women',
    website: 'https://www.igdtuw.ac.in',
    howToReach: {
      address: 'Madrasa Road, Kashmere Gate, New Delhi – 110006',
      details: [
        'Adjacent to Kashmere Gate metro station — a major interchange (Red / Yellow / Violet Lines)',
        'Kashmere Gate ISBT (inter-state bus terminal) is a short walk away',
        'Central Delhi location, well connected to most of the city',
      ],
    },
    ranking: {
      source: 'NIRF 2025',
      items: [
        { label: 'Engineering', value: 'Band 201–300' },
      ],
    },
    fees: {
      tuition: '≈ ₹5.2–8.6 lakh total (4-year B.Tech, varies by branch)',
      hostel: '≈ ₹1.6 lakh per year (mess + room + refundable deposit, women-only hostels)',
    },
    placement: {
      note: 'Figures vary by branch and year — treat as indicative, not guaranteed. IGDTUW admits women only.',
      companiesVisited: '≈200 companies visited in 2025, making ≈1,300 offers',
      highest: '≈ ₹1 Cr (2025); ≈ ₹56–76 LPA in a typical year',
      average: '≈ ₹18–25 LPA typical range',
      recruiters: ['Microsoft', 'Amazon', 'Adobe', 'Google', 'Deloitte', 'Intel'],
    },
  },
}

export const COLLEGE_ORDER = ['DTU', 'NSUT', 'IIITD', 'IGDTUW']
