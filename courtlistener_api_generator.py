import streamlit as st
import json
import re
import requests
from pprint import pprint
from mistralai import Mistral
import os


def main():
    st.title("CourtListener API URL generator")
    st.write("This is a prototype. The idea is to help generate API URL to CL based on a query in natural language.")

    query = st.text_input("Enter your search query:", placeholder='e.g., cases from kansas district court filed before 01/01/2020, ')

    if query:
        # any other good model (sonnet, gpt-4o) will work too. 
        api_key = "your_api_key"
        model = "mistral-large-latest"
        client = Mistral(api_key=api_key)

        prompt = '''You are a helpful assistant. Your goal is to turn user's query into an API call using the below guide: 

CourtListener API Query Construction Guide
Base URL: https://www.courtlistener.com/api/rest/v3/search/
Key Parameters:

type=o (for opinions)
order_by=score%20desc (sort by relevance)
case_name=[CASE NAME] (filter by case name)
stat_Precedential=on (for precedential cases)
court=[COURT IDENTIFIERS] (specify courts)
filed_after=[DATE] (filter by date, format: MM%2FDD%2FYYYY)

Court Identifiers:

Federal Courts:

Supreme Court: scotus
this query searches for decisions of all federal appellate courts where case name contains the word 'Oracle': 
?q=&type=o&order_by=score%20desc&case_name=Oracle&stat_Precedential=on&court=scotus%20ca1%20ca2%20ca3%20ca4%20ca5%20ca6%20ca7%20ca8%20ca9%20ca10%20ca11%20cadc%20cafc
 
this query searches for the same named case but within federal district courts:
?q=&type=o&order_by=score%20desc&case_name=Oracle&stat_Precedential=on&court=dcd%20almd%20alnd%20alsd%20akd%20azd%20ared%20arwd%20cacd%20caed%20cand%20casd%20cod%20ctd%20ded%20flmd%20flnd%20flsd%20gamd%20gand%20gasd%20hid%20idd%20ilcd%20ilnd%20ilsd%20innd%20insd%20iand%20iasd%20ksd%20kyed%20kywd%20laed%20lamd%20lawd%20med%20mdd%20mad%20mied%20miwd%20mnd%20msnd%20mssd%20moed%20mowd%20mtd%20ned%20nvd%20nhd%20njd%20nmd%20nyed%20nynd%20nysd%20nywd%20nced%20ncmd%20ncwd%20ndd%20ohnd%20ohsd%20oked%20oknd%20okwd%20ord%20paed%20pamd%20pawd%20rid%20scd%20sdd%20tned%20tnmd%20tnwd%20txed%20txnd%20txsd%20txwd%20utd%20vtd%20vaed%20vawd%20waed%20wawd%20wvnd%20wvsd%20wied%20wiwd%20wyd%20gud%20nmid%20prd%20vid%20californiad%20illinoised%20illinoisd%20indianad%20orld%20ohiod%20pennsylvaniad%20southcarolinaed%20southcarolinawd%20tennessed%20canalzoned

this query searches for the same case, also precedential status but among all state courts 
?q=&type=o&order_by=score%20desc&case_name=Oracle&stat_Precedential=on&court=ala%20alactapp%20alacrimapp%20alacivapp%20alaska%20alaskactapp%20ariz%20arizctapp%20ariztaxct%20ark%20arkctapp%20arkworkcompcom%20arkag%20cal%20calctapp%20calappdeptsuper%20calag%20colo%20coloctapp%20coloworkcompcom%20coloag%20conn%20connappct%20connsuperct%20connworkcompcom%20del%20delch%20delorphct%20delsuperct%20delctcompl%20delfamct%20deljudct%20dc%20fla%20fladistctapp%20flaag%20ga%20gactapp%20haw%20hawapp%20idaho%20idahoctapp%20ill%20illappct%20ind%20indctapp%20indtc%20iowa%20iowactapp%20kan%20kanctapp%20kanag%20ky%20kyctapp%20kyctapphigh%20la%20lactapp%20laag%20me%20mesuperct%20md%20mdctspecapp%20mdag%20mass%20massappct%20masssuperct%20massdistct%20masslandct%20maworkcompcom%20mich%20michctapp%20minn%20minnctapp%20minnag%20miss%20missctapp%20mo%20moctapp%20moag%20mont%20monttc%20montag%20neb%20nebctapp%20nebag%20nev%20nevapp%20nh%20nj%20njsuperctappdiv%20njtaxct%20njch%20nm%20nmctapp%20ny%20nyappdiv%20nyappterm%20nysupct%20nycountyctny%20nydistct%20nyjustct%20nyfamct%20nysurct%20nycivct%20nycrimct%20nyag%20nc%20ncctapp%20ncsuperct%20ncworkcompcom%20nd%20ndctapp%20ohio%20ohioctapp%20ohioctcl%20okla%20oklacivapp%20oklacrimapp%20oklajeap%20oklacoj%20oklaag%20or%20orctapp%20ortc%20pa%20pasuperct%20pacommwct%20cjdpa%20ri%20risuperct%20sc%20scctapp%20sd%20tenn%20tennctapp%20tenncrimapp%20tennworkcompcl%20tennworkcompapp%20tennsuperct%20tex%20texapp%20texcrimapp%20texreview%20texjpml%20texag%20utah%20utahctapp%20vt%20vtsuperct%20va%20vactapp%20wash%20washctapp%20washag%20washterr%20wva%20wvactapp%20wis%20wisctapp%20wisag%20wyo

this query searches for cases with name containing the word 'Oracle' among all courts, federal and state, without any limitation 
?q=&type=o&order_by=score%20desc&case_name=Oracle&stat_Precedential=on&filed_after=07%2F01%2F2020

this is an this is a correct example for the case name containing the word 'smith' from the federal courts of the first circuit filed after certain date: 
?q=&type=o&order_by=score%20desc&case_name=smith&stat_Precedential=on&filed_after=07%2F01%2F2010&court=ca1

Multiple courts: Separate with %20 (e.g., ca1%20ca2%20ca3)
All courts: Omit the 'court' parameter
More examples:

U.S. Supreme Court cases mentioning "Smith":
?q=&type=o&order_by=score%20desc&case_name=smith&stat_Precedential=on&court=scotus
Ninth Circuit cases mentioning "Oracle" filed after January 1, 2020:
?q=&type=o&order_by=score%20desc&case_name=Oracle&stat_Precedential=on&court=ca9&filed_after=01%2F01%2F2020
All federal appellate courts, precedential "Oracle" cases:
?q=&type=o&order_by=score%20desc&case_name=Oracle&stat_Precedential=on&court=scotus%20ca1%20ca2%20ca3%20ca4%20ca5%20ca6%20ca7%20ca8%20ca9%20ca10%20ca11%20cadc%20cafc
All Indiana state courts, "Smith" cases:
?q=&type=o&order_by=score%20desc&case_name=smith&stat_Precedential=on&court=ind%20indctapp%20indtc
Mississippi Supreme Court, "Smith" cases:
?q=&type=o&order_by=score%20desc&case_name=smith&stat_Precedential=on&court=miss
All Mississippi state courts, "Smith" cases:
?q=&type=o&order_by=score%20desc&case_name=smith&stat_Precedential=on&court=miss%20missctapp
Federal district court in Kansas, "Smith" cases:
?q=&type=o&order_by=score%20desc&case_name=smith&stat_Precedential=on&court=ksd
Southern District of Indiana, "Smith" cases:
?q=&type=o&order_by=score%20desc&case_name=smith&stat_Precedential=on&court=insd
All courts (federal and state), "Oracle" cases after July 1, 2020:
?q=&type=o&order_by=score%20desc&case_name=Oracle&stat_Precedential=on&filed_after=07%2F01%2F2020
All federal appellate courts looking for cases with name like 'Oracle' filed before 01/01/2020: 
?q=&type=o&order_by=score%20desc&case_name=Oracle&stat_Precedential=on&filed_before=01%2F01%2F2020&court=scotus%20ca1%20ca2%20ca3%20ca4%20ca5%20ca6%20ca7%20ca8%20ca9%20ca10%20ca11%20cadc%20cafc#
Looking for a case named like "Google v Oracle" from all federal apellate courts: 
?q=&type=o&order_by=score%20desc&case_name=Google%20v%20Oracle&stat_Precedential=on&filed_before=01%2F01%2F2020&court=scotus%20ca1%20ca2%20ca3%20ca4%20ca5%20ca6%20ca7%20ca8%20ca9%20ca10%20ca11%20cadc%20cafc
If user enters query like '750F.3d1339' or any other combination of words and numbers similar , it is most likely the user is looking for a case 
based on its citation. For example, this query searches for cases with specific citation: 
?type=o&q=&type=o&order_by=score%20desc&stat_Precedential=on&citation=750%20F.3d%201339
This query is searching for cases based on both name and citation: 
?q=&type=o&order_by=score%20desc&case_name=brown%20v%20board%20of%20education%20&stat_Precedential=on&citation=98%20F.Supp.%20797
This query is searching for cases from all courts based on judge's name 'Smith': 
?q=&type=o&order_by=score%20desc&judge=Smith&stat_Precedential=on
This query is searching for cases where user wants to exclude certain courts "abortion-related cases relying on roe v wade that aren't in the supreme court" 
?q=abortion%20%22roe%20v%20wade%22&type=o&order_by=score%20desc&stat_Precedential=on&court=ca1%20ca2%20ca3%20ca4%20ca5%20ca6%20ca7%20ca8%20ca9%20ca10%20ca11%20cadc%20cafc%20dcd%20almd%20alnd%20alsd%20akd%20azd%20ared%20arwd%20cacd%20caed%20cand%20casd%20cod%20ctd%20ded%20flmd%20flnd%20flsd%20gamd%20gand%20gasd%20hid%20idd%20ilcd%20ilnd%20ilsd%20innd%20insd%20iand%20iasd%20ksd%20kyed%20kywd%20laed%20lamd%20lawd%20med%20mdd%20mad%20mied%20miwd%20mnd%20msnd%20mssd%20moed%20mowd%20mtd%20ned%20nvd%20nhd%20njd%20nmd%20nyed%20nynd%20nysd%20nywd%20nced%20ncmd%20ncwd%20ndd%20ohnd%20ohsd%20oked%20oknd%20okwd%20ord%20paed%20pamd%20pawd%20rid%20scd%20sdd%20tned%20tnmd%20tnwd%20txed%20txnd%20txsd%20txwd%20utd%20vtd%20vaed%20vawd%20waed%20wawd%20wvnd%20wvsd%20wied%20wiwd%20wyd%20gud%20nmid%20prd%20vid%20californiad%20illinoised%20illinoisd%20indianad%20orld%20ohiod%20pennsylvaniad%20southcarolinaed%20southcarolinawd%20tennessed%20canalzoned%20bap1%20bap2%20bap6%20bap8%20bap9%20bap10%20bapme%20bapma%20almb%20alnb%20alsb%20akb%20arb%20areb%20arwb%20cacb%20caeb%20canb%20casb%20cob%20ctb%20deb%20dcb%20flmb%20flnb%20flsb%20gamb%20ganb%20gasb%20hib%20idb%20ilcb%20ilnb%20ilsb%20innb%20insb%20ianb%20iasb%20ksb%20kyeb%20kywb%20laeb%20lamb%20lawb%20meb%20mdb%20mab%20mieb%20miwb%20mnb%20msnb%20mssb%20moeb%20mowb%20mtb%20nebraskab%20nvb%20nhb%20njb%20nmb%20nyeb%20nynb%20nysb%20nywb%20nceb%20ncmb%20ncwb%20ndb%20ohnb%20ohsb%20okeb%20oknb%20okwb%20orb%20paeb%20pamb%20pawb%20rib%20scb%20sdb%20tneb%20tnmb%20tnwb%20tennesseeb%20txeb%20txnb%20txsb%20txwb%20utb%20vtb%20vaeb%20vawb%20waeb%20wawb%20wvnb%20wvsb%20wieb%20wiwb%20wyb%20gub%20nmib%20prb%20vib%20ala%20alactapp%20alacrimapp%20alacivapp%20alaska%20alaskactapp%20ariz%20arizctapp%20ariztaxct%20ark%20arkctapp%20arkworkcompcom%20arkag%20cal%20calctapp%20calappdeptsuper%20calag%20colo%20coloctapp%20coloworkcompcom%20coloag%20conn%20connappct%20connsuperct%20connworkcompcom%20del%20delch%20delorphct%20delsuperct%20delctcompl%20delfamct%20deljudct%20dc%20fla%20fladistctapp%20flaag%20ga%20gactapp%20haw%20hawapp%20idaho%20idahoctapp%20ill%20illappct%20ind%20indctapp%20indtc%20iowa%20iowactapp%20kan%20kanctapp%20kanag%20ky%20kyctapp%20kyctapphigh%20la%20lactapp%20laag%20me%20mesuperct%20md%20mdctspecapp%20mdag%20mass%20massappct%20masssuperct%20massdistct%20masslandct%20maworkcompcom%20mich%20michctapp%20minn%20minnctapp%20minnag%20miss%20missctapp%20mo%20moctapp%20moag%20mont%20monttc%20montag%20neb%20nebctapp%20nebag%20nev%20nevapp%20nh%20nj%20njsuperctappdiv%20njtaxct%20njch%20nm%20nmctapp%20ny%20nyappdiv%20nyappterm%20nysupct%20nycountyctny%20nydistct%20nyjustct%20nyfamct%20nysurct%20nycivct%20nycrimct%20nyag%20nc%20ncctapp%20ncsuperct%20ncworkcompcom%20nd%20ndctapp%20ohio%20ohioctapp%20ohioctcl%20okla%20oklacivapp%20oklacrimapp%20oklajeap%20oklacoj%20oklaag%20or%20orctapp%20ortc%20pa%20pasuperct%20pacommwct%20cjdpa%20ri%20risuperct%20sc%20scctapp%20sd%20tenn%20tennctapp%20tenncrimapp%20tennworkcompcl%20tennworkcompapp%20tennsuperct%20tex%20texapp%20texcrimapp%20texreview%20texjpml%20texag%20utah%20utahctapp%20vt%20vtsuperct%20va%20vactapp%20wash%20washctapp%20washag%20washterr%20wva%20wvactapp%20wis%20wisctapp%20wisag%20wyo%20ag%20afcca%20asbca%20armfor%20acca%20uscfc%20tax%20bia%20olc%20mc%20mspb%20nmcca%20cavc%20bva%20fiscr%20fisc%20cit%20usjc%20jpml%20cc%20com%20ccpa%20cusc%20bta%20eca%20tecoa%20reglrailreorgct%20kingsbench
This query searches for cases that cite certain other cases "find cases that cite 108713 OR 9425157 OR 9425158 OR 9425159"
?q=cites:(108713%20OR%209425157%20OR%209425158%20OR%209425159)

Remember:
Always URL-encode spaces (%20) and special characters in the query.
The API is flexible, allowing for broad or narrow searches across various jurisdictions and date ranges.
When in doubt about state court identifiers, use the state abbreviation for the highest court and [state]ctapp for the appellate court.
Some states may have unique identifiers for their court systems. Always double-check for specific states if unsure.

Adjust parameters based on user needs. This structure allows for precise querying of legal opinions across different jurisdictions and time periods.

Present the response in json format with 'api_url' as a key '''

        chat_response = client.chat.complete(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": query}
            ]
        )

        response_content = chat_response.choices[0].message.content
        #st.write(response_content)

        # Extract JSON from the message content and parse it
        json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                api_url = data.get('api_url')
                if api_url:
                    st.write(f"Generated API URL: {api_url}")
                else:
                    st.error("API URL not found in the generated data")
            except json.JSONDecodeError:
                st.error("Invalid JSON format in the response")
        else:
            st.error("No valid JSON found in the response")

if __name__ == "__main__":
    main()
